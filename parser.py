
from ast import parse
from dataclasses import dataclass
from enum import Enum, auto
import re
from typing import List, Tuple

from misc import not_implemented


class Primitives(Enum):
    Int = auto()
    Bool = auto()
    Struct = auto()
    Func = auto()
    Unknown = auto()


class OpType(Enum):

    # Allocates memory and declare local varibales
    OpBeginScope = auto()

    # Deallocates memory
    OpEndScope = auto()

    # Push oprands to stack
    OpPush = auto()

    # Evaluates what is on top of the stack
    OpEval = auto()

    # Assignment and evalution of whatever is on the stack
    OpMov = auto()

    # Print intrinstic prints whatever is at the top of stack
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


def parse_int_liternal(symbol: str) -> tuple[int, bool]:
    i = 1
    num = 0

    for d in symbol:
        if not d.isdigit():
            return 0,  False

        num = num + int(d) * i
        i = i * 10

    return num, True


def parse_expression(exp: str, program: Program) -> tuple[List[str], List[Primitives]]:
    eval_stack = []
    type_stack = []
    exp = "$" + exp

    i = 1
    num = 0
    name = ""

    evaluating_int_literal = False
    evaluating_variable = False

    for ch in exp[::-1]:

        if ch.isdigit() and not evaluating_variable:
            num = num + int(ch) * i
            i = i * 10
            evaluating_int_literal = True

        elif ch.isalpha():
            if evaluating_int_literal:
                name = ch + str(num)
            else:
                name = ch + name

                evaluating_int_literal = False
                evaluating_variable = True

        elif ch in "+-/*%()":
            if evaluating_int_literal:
                eval_stack.append(num)
                type_stack.append(Primitives.Int)
            elif evaluating_variable:
                op_index, p_index = find_scope_with_symbol(name, program)

                if op_index != -1:
                    type = program.operations[op_index].types[p_index]
                    eval_stack.append(name)
                    type_stack.append(type)
                else:
                    op = program.operations[op]
                    print(
                        f"{op.file_path}:{op.line_num}:")
                    print(
                        f"Parsing Error : unrecognised symbol varible `{name}`")
                    exit(1)

            i = 1
            num = 0
            name = ""
            evaluating_int_literal = False
            evaluating_variable = False

            eval_stack.append(ch)
            type_stack.append(Primitives.Func)

        elif ch == "$":
            if evaluating_int_literal:
                eval_stack.append(num)
                type_stack.append(Primitives.Int)
            elif evaluating_variable:
                op_index, p_index = find_scope_with_symbol(name, program)

                if op_index != -1:
                    type = program.operations[op_index].types[p_index]
                    eval_stack.append(name)
                    type_stack.append(type)
                else:
                    op = program.operations[op_index]
                    print(
                        f"{op.file}:{op.line}:")
                    print(
                        f"Parsing Error : unrecognised symbol varible `{name}`")
                    exit(1)
            break

        elif ch == " ":
            pass

        else:
            print(
                f"Parsing Error : unrecognised symbol {ch}")
            exit(1)

    return eval_stack, type_stack


def match_primitives(primitive: str) -> Primitives:
    if primitive == "int":
        return Primitives.Int
    elif primitive == "bool":
        return Primitives.Bool

    return Primitives.Unknown


def get_symbol_types(symbols: List[str], program:Program) -> List[Primitives]:
    primitives = []

    for symbol in symbols:
    
        _, is_int_literal = parse_int_liternal(symbol)
        
        if is_int_literal:
            primitives.append(Primitives.Int)
            continue

        op_index,p_index = find_scope_with_symbol(symbol, program)
        
        if op_index != -1:
            primitives.append(program.operations[op_index].types[p_index])
            continue
        
        primitives.append(Primitives.Unknown)

    return primitives


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
                eval_stack, types = parse_expression(right_side, program)

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

                    var_type = match_primitives(var_info[1])

                    if var_type == Primitives.Unknown:
                        print(f"{file_path}:{line_num}:")
                        print(f"Parsing Error: unkown type `{var_info[1]}`")
                        exit(1)

                    op_index = find_local_scope(program)

                    program.operations[op_index].oprands.append(var_name)
                    program.operations[op_index].types.append(var_type)
                else:
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

                types = get_symbol_types(tokens, program)

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

    for op in program.operations:
        print(f"{op.file}:{op.line}:", op.type, op.oprands, op.types)

    return program
