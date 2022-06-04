
from ast import parse
from dataclasses import dataclass
from enum import Enum, auto
from pprint import pprint
import re
from typing import List, Tuple

from misc import not_implemented


class Primitives(Enum):
    I32 = auto()
    I64 = auto()
    F32 = auto()
    F64 = auto()
    Bool = auto()
    Struct = auto()
    Func = auto()
    Unknown = auto()


class OpType(Enum):

    # Declare local varibales
    OpBeginScope = auto()

    # Removes all local variables
    OpEndScope = auto()

    # Push oprands to a compile time stack
    OpPush = auto()

    # Assignment and evalution of whatever is on the compile time stack
    OpMov = auto()

    # Jumps to end of the block if the conditions are not me
    OpIf = auto()

    # Print intrinstic prints whatever is at the top of compile time stack
    OpPrint = auto()


@dataclass
class Operation:
    type: OpType
    file: str
    line: int
    oprands: List[int | str]  # they can be both integers and string atm
    types: List[Primitives]


@dataclass
class Program:
    operations: List[Operation]


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

    return Primitives.Unknown


def parse_int_liternal(symbol: str) -> tuple[int, bool]:
    i = 1
    num = 0

    for d in symbol:
        if not d.isdigit():
            return 0,  False

        num = num * i + int(d)
        i = i * 10

    return num, True


def parse_bool_literal(symbol: str) -> tuple[int, bool]:
    if symbol == "true":
        return 1, True
    elif symbol == "false":
        return 0, True

    return 0, False


def find_scope_with_symbol(symbol: str, program: Program) -> tuple[int, int]:
    l = len(program.operations)

    skip = False
    for i, op in enumerate(program.operations[::-1]):
        if op.type == OpType.OpBeginScope:
            if not skip:
                if symbol in op.oprands:
                    return l-(i+1), op.oprands.index(symbol)
            skip = False
        elif op.type == OpType.OpBeginScope:
            skip = True

    return -1, -1


def find_local_scope(program: Program) -> int:
    l = len(program.operations)

    for i, op in enumerate(program.operations[::-1]):
        if op.type == OpType.OpBeginScope:
            return l-(i+1)

    return -1


def parse_word(word: str, program: Program, file: str, line: int) -> tuple[int | str, Primitives]:
    num, is_int = parse_int_liternal(word)
    what_bool, is_bool_literal = parse_bool_literal(word)
    op_index, p_index = find_scope_with_symbol(word, program)

    # Match int literals
    if is_int:
        return num, Primitives.I64

    # Match bool literals
    elif is_bool_literal:
        return what_bool, Primitives.Bool

    # Match variables
    elif op_index != -1:
        type = program.operations[op_index].types[p_index]

        return word, type

    else:
        print(
            f"{file}:{line}:")
        print(
            f"Parsing Error : unrecognised word `{word}`")
        exit(1)


def operator_type(operator: str) -> Primitives:
    if operator in ["+", "-", "*", "%"]:
        return Primitives.I64
    elif operator in ["/"]:
        return Primitives.F64
    elif operator in ["!", "<", ">", "&&", "||"]:
        return Primitives.Bool

    return Primitives.Unknown


def parse_expression(exp: str, program: Program, file: str, line: int) -> tuple[List[int | str], List[Primitives]]:
    eval_stack: List[int | str] = []
    type_stack: List[Primitives] = []

    exp = exp + "$"

    word = ""
    operator = ""

    for ch in exp:

        # Matching operators
        if ch in "+-/*%()!&()|<>":
            if word != "":
                eval, type = parse_word(word, program, file, line)

                eval_stack.append(eval)
                type_stack.append(type)

                word = ""

            operator = operator + ch

            if operator in ["+", "-", "/", "*", "%", "!", "<", ">", "&&", "||", "(", ")"]:
                eval_stack.append(operator)
                type_stack.append(operator_type(operator))

                operator = ""

        elif ch == "$":
            if word != "":
                eval, type = parse_word(word, program, file, line)

                eval_stack.append(eval)
                type_stack.append(type)

        elif ch == " ":
            pass

        else:
            word = word + ch

    return eval_stack, type_stack


def get_symbol_types(symbols: List[str], program: Program) -> tuple[List[int | str], List[Primitives]]:
    primitives = []

    for i, symbol in enumerate(symbols):

        _, is_int_literal = parse_int_liternal(symbol)

        if is_int_literal:
            symbols[i] = int(symbol)
            primitives.append(Primitives.I64)
            continue

        op_index, p_index = find_scope_with_symbol(symbol, program)

        if op_index != -1:
            primitives.append(program.operations[op_index].types[p_index])
            continue

        primitives.append(Primitives.Unknown)

    return symbols, primitives


def parse_program_from_file(file_path) -> Program:
    program = Program(operations=[])

    with open(file_path) as file:
        lines = re.split("[\n]", file.read())

        # Initialize the global scope
        program.operations.append(
            Operation(OpType.OpBeginScope, file_path, 1, [], []))

        for line_num, line in enumerate(lines):

            line = line.split("//")[0].strip()
            line_num = line_num + 1

            # Skip empty lines
            if line == "":
                continue

            #  Matching Assignments
            elif re.fullmatch("[a-zA-Z][a-zA-Z0-9_]*:?[a-zA-Z]?[a-zA-Z0-9]*?[ ]*=.*", line):
                tokens = re.split("[ ]*=[ ]*", line)

                if len(tokens) > 2:
                    print(f"{file_path}:{line_num}:")
                    print(
                        "Parsing Error: muliple '=' found on right side of an assignment")
                    exit(1)

                left_side = tokens[0]
                right_side = tokens[1]

                var_info = left_side.split(":")
                var_name = var_info[0]

                # assignment
                eval_stack, types = parse_expression(
                    right_side, program, file_path, line_num)

                program.operations.append(
                    Operation(OpType.OpPush, file_path, line_num, eval_stack, types))

                op_index, _ = find_scope_with_symbol(var_name, program)

                var_type = Primitives.Unknown

                # declaration
                if op_index == -1:
                    if len(var_info) != 2:
                        print(f"{file_path}:{line_num}:")
                        print(
                            f"Parsing Error: expected type when declaring a variable")
                        exit(1)

                    var_type = parse_primitives(var_info[1])

                    if var_type == Primitives.Unknown:
                        print(f"{file_path}:{line_num}:")
                        print(f"Parsing Error: unkown type `{var_info[1]}`")
                        exit(1)

                    op_index = find_local_scope(program)

                    program.operations[op_index].oprands.append(var_name)
                    program.operations[op_index].types.append(var_type)
                else:
                    # TODO: allow casting maybe?

                    if len(var_info) != 1:
                        print(f"{file_path}:{line_num}:")
                        print(
                            f"Parsing Error: cannot redefine types for declared variables")
                        exit(1)

                var_type = program.operations[op_index].types[-1]
                program.operations.append(
                    Operation(OpType.OpMov, file_path, line_num, [var_name], [var_type]))

            # Matching print intrinsic
            elif re.fullmatch("print[ ]+.*", line):
                tokens = re.split(" ", line)
                tokens.pop(0)

                tokens, types = get_symbol_types(tokens, program)

                if Primitives.Unknown in types:
                    index = types.index(Primitives.Unknown)

                    print(f"{file_path}:{line_num}:")
                    print(
                        f"Parsing Error: unknown symbol {tokens[index]}")
                    exit(1)

                program.operations.append(
                    Operation(OpType.OpPrint, file_path, line_num, tokens, types))

                pass

            # Other
            else:
                print(f"{file_path}:{line_num}:")
                print(f"Parsing Error: unexpected token `{line}`")
                exit(1)

        # End the global scope
        program.operations.append(
            Operation(OpType.OpEndScope, file_path, len(lines), [], []))

    return program
