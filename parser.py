from dataclasses import dataclass
from enum import Enum, auto
from pprint import pprint
import re
from typing import List
from lexer import Token, lex_source

from misc import not_implemented, operator_list, report_error
from static_types import Primitives, TypedPtr, Types, size_of_primitive


class OpType(Enum):

    # Declare local varibales
    OpBeginScope = auto()

    # Removes all local variables
    OpEndScope = auto()

    # Push oprands to a compile time stack
    OpPush = auto()

    # Assignment and evalution of whatever is on the compile time stack
    OpMov = auto()

    # Jumps to end of the block if the condition pushed to slack is false
    OpIf = auto()

    OpElseIf = auto()

    # Jumps to end of the block body
    OpElse = auto()

    # Jumps back to while if condition is true or else jumps to end
    OpWhile = auto()

    # Print intrinstic prints whatever is at the top of compile time stack
    OpPrint = auto()


@dataclass
class Operation:
    type: OpType
    file: str
    line: int
    oprands: List[int | str]  # they can be both integers and string atm
    types: List[Types]


@dataclass
class Memory:
    count: int
    primitive: Primitives


@dataclass
class Program:
    global_memory_ptr: int
    global_memory_capacity: int
    operations: List[Operation]


def find_scope_with_symbol(symbol: str, program: Program) -> tuple[int, int]:
    l = len(program.operations)

    skip = False
    for i, op in enumerate(program.operations[::-1]):
        if op.type == OpType.OpBeginScope:
            if not skip:
                if symbol in op.oprands:
                    return l-(i+1), op.oprands.index(symbol)
            skip = False
        elif op.type == OpType.OpEndScope:
            skip = True

    return -1, -1


def find_local_scope(program: Program) -> int:
    l = len(program.operations)

    skip = False
    for i, op in enumerate(program.operations[::-1]):
        if op.type == OpType.OpBeginScope:
            if not skip:
                return l-(i+1)
            skip = False
        elif op.type == OpType.OpEndScope:
            skip = True

    return -1


def alloc_mem(size: int, program: Program) -> int:
    loc = program.global_memory_ptr
    program.global_memory_ptr += size

    i = find_local_scope(program)
    program.operations[i].oprands[0] += size

    if program.global_memory_ptr > program.global_memory_capacity:
        program.global_memory_capacity += size

    return loc


def parse_primitives(primitive: str) -> Primitives:
    if primitive == "i32":
        return Primitives.I32
    elif primitive == "i64":
        return Primitives.I64
    elif primitive == "f32":
        return Primitives.F32
    elif primitive == "f64":
        return Primitives.F64
    elif primitive == "bool":
        return Primitives.Bool
    elif primitive == "byte":
        return Primitives.Byte

    return Primitives.Unknown


def parse_int_literal(symbol: str) -> tuple[int, bool]:
    num = 0

    for d in symbol:
        if not d.isdigit():
            return 0,  False

        num = num * 10 + int(d)

    return num, True


def parse_bool_literal(symbol: str) -> tuple[int, bool]:
    if symbol == "true":
        return 1, True
    elif symbol == "false":
        return 0, True

    return 0, False


def parse_word(word: str, program: Program, file: str, line: int) -> tuple[int | str, Types]:
    word = word.strip()

    num, is_int = parse_int_literal(word)
    what_bool, is_bool_literal = parse_bool_literal(word)
    op_index, p_index = find_scope_with_symbol(word, program)

    # Match int literals
    if is_int:
        return num, Primitives.I64

    # Match bool literals
    elif is_bool_literal:
        return what_bool, Primitives.Bool

    # Match objects
    elif re.fullmatch(".*\{\}", word):
        tokens: List[tuple] = re.findall("(.*)\{(.*)\}", word)
        tp = tokens.pop()

        # TODO: parse what's inside struct

        if len(tp) != 2:
            report_error(
                f"no type found for struct", file, line)

        primitive = parse_primitives(tp[0].strip())
        if primitive == Primitives.Unknown:
            report_error(
                f"unknown type `{tp[0]}`", file, line)

        return alloc_mem(size_of_primitive(primitive), program), TypedPtr(primitive)

    # Match arrays
    elif re.fullmatch("\[[0-9]+\].*", word):
        tokens: List[tuple] = re.findall("\[(.*)\](.*)", word)
        tp = tokens.pop()

        if len(tp) != 2:
            report_error(
                f"no type found for arrays", file, line)

        size, _ = parse_int_literal(tp[0])

        primitive = parse_primitives(tp[1].strip())
        if primitive == Primitives.Unknown:
            report_error(
                f"unknown type `{tp[0]}`", file, line)

        return alloc_mem(size_of_primitive(primitive) * size, program), TypedPtr(primitive)

    # Match characters
    elif re.fullmatch("'\\\?.'", word):
        tokens: List[str] = re.findall("'(\\\?.)'", word)

        if len(tokens) == 1:
            char = tokens.pop()

            # Handling character escape
            if char == '\\n':
                char = '\n'
            elif char == '\\\'':
                char = '\''
            elif char == '\\b':
                char = ' '

            return ord(char), Primitives.Byte
        else:
            report_error(
                f"no character inside character brackets", file, line)

    # Match variables
    elif op_index != -1:
        type = program.operations[op_index].types[p_index]
        return word, type

    else:
        report_error("unrecognised word `{word}`", file, line)


def parse_expression(exp: str, program: Program, file: str, line: int) -> tuple[List[int | str], List[Types]]:
    eval_stack: List[int | str] = []
    type_stack: List[Primitives] = []

    word = ""
    operator = ""

    for i, ch in enumerate(exp):

        # Matching operators
        if ch in "=+-/*%()!&^|<>":
            if word != "":
                eval, type = parse_word(word, program, file, line)

                eval_stack.append(eval)
                type_stack.append(type)

                word = ""

            operator = operator + ch
            if operator in operator_list:
                eval_stack.append(operator)
                type_stack.append(Primitives.Operator)

                operator = ""

        elif ch == " ":
            pass

        else:
            word = word + ch

        if i == len(exp) - 1:
            if word != "":
                eval, type = parse_word(word, program, file, line)

                eval_stack.append(eval)
                type_stack.append(type)

    return eval_stack, type_stack


def consume_token(tokens: List[Token], i: List[int]) -> Token | None:
    if i[0] >= len(tokens):
        return None
    token = tokens[i[0]]
    i[0] = i[0] + 1
    return token


def peek_token(tokens: List[Token], i: List[int]) -> Token | None:
    if i[0] >= len(tokens):
        return None
    token = tokens[i[0]]
    return token


keywords = ["if", "while", "else", "print", "{", "}"]


def parse_program_from_file(file_path: str) -> Program:
    tokens = lex_source(file_path)

    program = Program(global_memory_ptr=1,
                      global_memory_capacity=1, operations=[])

    program.operations.append(
        Operation(OpType.OpBeginScope, file_path, 1, [0], [Primitives.Unknown]))

    state = [0]
    while state[0] < len(tokens):
        token = consume_token(tokens, state)

        if token.word in keywords:
            if token.word == "if":
                token = consume_token(tokens, state)

                eval_stack, types = parse_expression(
                    token.word, program, token.file, token.line)

                program.operations.append(
                    Operation(OpType.OpPush, token.file, token.line, eval_stack, types))

                program.operations.append(
                    Operation(OpType.OpIf, token.file, token.line, [], []))

            elif token.word == "else":

                top_op = program.operations[-1]

                if top_op.type != OpType.OpEndScope:
                    report_error("unexpected expression else",
                                 token.file, token.line)

                skip = False
                if_found = False
                for op in program.operations[::-1]:
                    if op.type == OpType.OpElse:
                        skip = True
                    elif op.type == OpType.OpIf:
                        if not skip:
                            if_found = True
                            break

                        skip = False

                if not if_found:
                    report_error("unexpected else without if",
                                 token.file, token.line)

                next_token = peek_token(tokens, state)

                if next_token.word == "if":  # elseif
                    consume_token(tokens, state)
                    token = consume_token(tokens, state)

                    eval_stack, types = parse_expression(
                        token.word, program, token.file, token.line)

                    program.operations.append(
                        Operation(OpType.OpPush, token.file, token.line, eval_stack, types))

                    program.operations.append(
                        Operation(OpType.OpElseIf, token.file, token.line, [], []))
                else:
                    program.operations.append(
                        Operation(OpType.OpElse, token.file, token.line, [], []))

            elif token.word == "while":
                token = consume_token(tokens, state)

                eval_stack, types = parse_expression(
                    token.word, program, token.file, token.line)

                program.operations.append(
                    Operation(OpType.OpPush, token.file, token.line, eval_stack, types))

                program.operations.append(
                    Operation(OpType.OpWhile, token.file, token.line, [], []))

            elif token.word == "{":
                program.operations.append(
                    Operation(OpType.OpBeginScope, token.file, token.line, [0], [Primitives.Unknown]))

            elif token.word == "}":
                i = 0
                j = 0
                op_type = OpType.OpIf

                for ip, op in enumerate(program.operations[::-1]):
                    if op.type in [OpType.OpIf, OpType.OpWhile, OpType.OpElseIf, OpType.OpElse] and len(op.oprands) == 0:
                        op.oprands.append(i+1)
                        op_type = op.type
                        j = len(program.operations) - (ip + 1)
                        break

                    i = i+1
                stack = []

                if op_type == OpType.OpWhile:
                    stack = [j - 1]

                elif op_type == OpType.OpIf:
                    stack = []

                i = find_local_scope(program)
                program.global_memory_ptr -= program.operations[i].oprands[0]

                program.operations.append(
                    Operation(OpType.OpEndScope, token.file, token.line, stack, []))
                pass

            elif token.word == "print":
                token = consume_token(tokens, state)

                eval_stack, types = parse_expression(
                    token.word, program, token.file, token.line)

                program.operations.append(
                    Operation(OpType.OpPush, token.file, token.line, eval_stack, types))

                program.operations.append(
                    Operation(OpType.OpPrint, token.file, token.line, [], []))
                pass
        else:
            next_token = peek_token(tokens, state)
            if next_token is not None:
                tp = Primitives.Unknown
                deref = False

                word = token.word
                file = token.file
                line = token.line

                if word[0] == "^":
                    word = word[1:]
                    deref = True

                ip, opi = find_scope_with_symbol(word, program)

                if ip == -1:
                    if next_token.word != ":":
                        report_error(f"Symbol `{word}` used before declaration",
                                     token.file, token.line)

                    consume_token(tokens, state)
                    next_token = peek_token(tokens, state)

                    if next_token.word != "=":
                        token = consume_token(tokens, state)

                        if token.word[0] == "^":
                            tp = TypedPtr(parse_primitives(
                                token.word[1:]))
                        else:
                            tp = parse_primitives(next_token.word)

                        if tp == Primitives.Unknown:
                            report_error(
                                f"unkown type `{token.word}`",
                                token.file, token.line)

                        ip = find_local_scope(program)

                        program.operations[ip].oprands.append(word)
                        program.operations[ip].types.append(tp)
                    else:
                        not_implemented("type inference")
                else:
                    tp = program.operations[ip].types[opi]

                next_token = peek_token(tokens, state)
                if next_token is not None and next_token.word == "=":
                    consume_token(tokens, state)
                    token = consume_token(tokens, state)

                    if token.word == "":
                        report_error("expected expression after `=`", token.file, token.line)

                    eval_stack, types = parse_expression(
                        token.word, program, token.file, token.line)

                    program.operations.append(
                        Operation(OpType.OpPush, token.file,
                                  token.line, eval_stack, types))

                    program.operations.append(
                        Operation(OpType.OpMov, token.file,
                                  token.line, [deref, word], [tp]))

            else:
                report_error(f"Expected token after `{token.word}`",
                             file, line)

    program.operations.append(
        Operation(OpType.OpEndScope, file_path, tokens[-1].line, [], []))

    return program
