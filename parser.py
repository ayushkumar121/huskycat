from dataclasses import dataclass
from enum import Enum, auto
import re
from typing import List, Type

from misc import not_implemented, operator_list
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
    global_memory: int
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

    skip = False
    for i, op in enumerate(program.operations[::-1]):
        if op.type == OpType.OpBeginScope:
            if not skip:
                return l-(i+1)
            skip = False
        elif op.type == OpType.OpEndScope:
            skip = True

    return -1


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
    elif primitive == "ptr":
        return Primitives.Ptr

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
            print(
                f"{file}:{line}:")
            print(
                f"Parsing Error : no type found for struct")
            exit(1)


        primitive =  parse_primitives(tp[0])
        if primitive == Primitives.Unknown:
            print(
                f"{file}:{line}:")
            print(
                f"Parsing Error : unknown type `{tp[0]}`")
            exit(1)

        loc = program.global_memory
        program.global_memory += size_of_primitive(primitive)

        return loc, TypedPtr(primitive)

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
            print(
                f"{file}:{line}:")
            print(
                f"Parsing Error : no character inside character brackets")
            exit(1)

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


# TODO: implement const eval
def const_eval(exp: str, program: Program, file: str, line: int) -> tuple[int | str, Types]:
    value, val_type = parse_word(exp, program, file, line)

    if type(value) != type(0):
        print(f"{file}:{line}:")
        print(
            f"Parsing Error: unsupported symbol in constant evaluation")
        exit(1)

    return value, val_type


def parse_program_from_file(file_path) -> Program:
    program = Program(global_memory=1, operations=[])

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

            #  Matching Declaration
            elif re.fullmatch("[a-zA-Z][a-zA-Z0-9_]*:\^?[a-zA-Z][a-zA-Z0-9]*", line):
                tokens = re.split(":", line)

                var_name = tokens[0]
                var_tp = tokens[1]

                i, j = find_scope_with_symbol(var_name, program)

                var_type = Primitives.Unknown

                if i == -1:
                    if var_tp[0] == "^":                     
                        primitive = parse_primitives(var_tp[1:])

                        if primitive == Primitives.Unknown:
                            print(f"{file_path}:{line_num}:")
                            print(f"Parsing Error: unknown type `{var_tp}`")
                            exit(1)

                        var_type = TypedPtr(primitive)
                    else:
                        var_type = parse_primitives(var_tp)
                        pass


                    if var_type == Primitives.Unknown:
                        print(f"{file_path}:{line_num}:")
                        print(f"Parsing Error: unknown type `{var_tp}`")
                        exit(1)

                    i = find_local_scope(program)

                    program.operations[i].oprands.append(var_name)
                    program.operations[i].types.append(var_type)
                else:
                    print(f"{file_path}:{line_num}:")
                    print(f"Parsing Error: variable `{var_tp}` already declared")
                    exit(1)

            #  Matching Assignments
            elif re.fullmatch("\^?[a-zA-Z][a-zA-Z0-9_]*:?\^?[a-zA-Z]?[a-zA-Z0-9]*?[ ]*=.*", line):
                deref = False
                tokens = re.split("[ ]*=[ ]*", line)

                if len(tokens) > 2:
                    print(f"{file_path}:{line_num}:")
                    print(
                        "Parsing Error: muliple '=' found on right side of an assignment")
                    exit(1)

                left_side: str = tokens[0]
                right_side: str = tokens[1]

                if left_side[0] == "^":
                    left_side = left_side[1:]
                    deref = True

                var_info = left_side.split(":")
                var_name = var_info[0]

                # parsing right side of an assignment
                if re.fullmatch("resb .+", right_side.strip()):
                    exp: List[str] = re.findall("resb (.+)", line)

                    val, tp = const_eval(
                        exp.pop(), program, file_path, line_num)

                    program.operations.append(
                        Operation(OpType.OpPush, file_path, line_num, [program.global_memory], [Primitives.Ptr]))

                    program.global_memory += val
                else:
                    eval_stack, types = parse_expression(
                        right_side, program, file_path, line_num)

                    program.operations.append(
                        Operation(OpType.OpPush, file_path, line_num, eval_stack, types))

                i, j = find_scope_with_symbol(var_name, program)

                var_type = Primitives.Unknown

                # declaration
                if i == -1:
                    if len(var_info) != 2:
                        print(f"{file_path}:{line_num}:")
                        print(
                            f"Parsing Error: expected type when declaring a variable")
                        exit(1)

                    if var_info[1][0] == "^":                     
                        primitive = parse_primitives(var_info[1][1:])

                        if primitive == Primitives.Unknown:
                            print(f"{file_path}:{line_num}:")
                            print(f"Parsing Error: unknown type `{var_info[1]}`")
                            exit(1)

                        var_type = TypedPtr(primitive)
                    else:
                        var_type = parse_primitives(var_info[1])


                    if var_type == Primitives.Unknown:
                        print(f"{file_path}:{line_num}:")
                        print(f"Parsing Error: unknown type `{var_info[1]}`")
                        exit(1)

                    i = find_local_scope(program)

                    program.operations[i].oprands.append(var_name)
                    program.operations[i].types.append(var_type)
                else:
                    if len(var_info) != 1:
                        print(f"{file_path}:{line_num}:")
                        print(
                            f"Parsing Error: cannot redefine types for declared variables")
                        exit(1)

                var_type = program.operations[i].types[j]

                if deref and var_type != Primitives.Ptr and type(var_type) != TypedPtr:
                    print(var_type, type(var_type) == TypedPtr)
                    print(f"{file_path}:{line_num}:")
                    print(
                        f"Parsing Error: cannot deref non ptr values")
                    exit(1)

                program.operations.append(
                    Operation(OpType.OpMov, file_path, line_num, [deref, var_name], [var_type]))
 
            # Matching if keyword
            elif re.fullmatch("if .*{", line):
                tokens = re.findall("if (.*){", line)

                eval_stack, types = parse_expression(
                    tokens.pop(), program, file_path, line_num)

                program.operations.append(
                    Operation(OpType.OpPush, file_path, line_num, eval_stack, types))

                program.operations.append(
                    Operation(OpType.OpIf, file_path, line_num, [], []))

                program.operations.append(
                    Operation(OpType.OpBeginScope, file_path, line_num, [], []))

            # Matching elif keyword
            elif re.fullmatch("else if .*{", line):
                top_op = program.operations[-1]

                if top_op.type != OpType.OpEndScope:
                    print(f"{file_path}:{line_num}:")
                    print(f"Parsing Error: unexpected expression else if")
                    exit(1)                                            
                 

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
                    print(f"{file_path}:{line_num}:")
                    print(f"Parsing Error: unexpected else if without if")
                    exit(1)                                            


                tokens = re.findall("else if (.*){", line)

                eval_stack, types = parse_expression(
                    tokens.pop(), program, file_path, line_num)

                program.operations.append(
                    Operation(OpType.OpPush, file_path, line_num, eval_stack, types))

                program.operations.append(
                    Operation(OpType.OpElseIf, file_path, line_num, [], []))

                program.operations.append(
                    Operation(OpType.OpBeginScope, file_path, line_num, [], []))

            # Matching else keyword
            elif re.fullmatch("else.*{", line):
                
                top_op = program.operations[-1]

                if top_op.type != OpType.OpEndScope:
                    print(f"{file_path}:{line_num}:")
                    print(f"Parsing Error: unexpected expression else")
                    exit(1)            

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
                    print(f"{file_path}:{line_num}:")
                    print(f"Parsing Error: unexpected else without if")
                    exit(1)                                            

                program.operations.append(
                    Operation(OpType.OpElse, file_path, line_num, [], []))

                program.operations.append(
                    Operation(OpType.OpBeginScope, file_path, line_num, [], []))

            # Matching while keyword
            elif re.fullmatch("while .*{", line):
                tokens = re.findall("while (.*){", line)

                eval_stack, types = parse_expression(
                    tokens.pop(), program, file_path, line_num)

                program.operations.append(
                    Operation(OpType.OpPush, file_path, line_num, eval_stack, types))

                program.operations.append(
                    Operation(OpType.OpWhile, file_path, line_num, [], []))

                program.operations.append(
                    Operation(OpType.OpBeginScope, file_path, line_num, [], []))

            # Matching end of blocks
            elif re.fullmatch("}", line):
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

                program.operations.append(
                    Operation(OpType.OpEndScope, file_path, line_num, stack, []))

            # Matching print intrinsic
            elif re.fullmatch("print .+", line):
                exp: List[str] = re.findall("print (.+)", line)

                eval_stack, types = parse_expression(
                    exp.pop(), program, file_path, line_num)

                program.operations.append(
                    Operation(OpType.OpPush, file_path, line_num, eval_stack, types))

                program.operations.append(
                    Operation(OpType.OpPrint, file_path, line_num, [], []))
          
            # Other
            else:
                print(f"{file_path}:{line_num}:")
                print(f"Parsing Error: unexpected token `{line}`")
                exit(1)

        # End the global scope
        program.operations.append(
            Operation(OpType.OpEndScope, file_path, len(lines), [], []))

    # not_implemented("else if parsing")
    return program
