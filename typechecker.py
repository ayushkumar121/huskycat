from typing import List
from misc import operator_predence, operator_list, binary_operators, unary_operators
from parser import OpType, Program
from static_types import Primitives, Types, type_str

def apply_op_binary(a: Types, b: Types, op: str) -> Types:
    if op in ["+",  "-", "*", "/"]:
        return b
    elif op == "%":
        return Primitives.I64
    elif op in ["||", "&&", ">", "<", "=="]:
        return Primitives.Bool

    return Primitives.Unknown


def apply_op_uinary(a: int, op: str) -> Types:
    if op == "!":
        return Primitives.Bool
    elif op == "^":
        return Primitives.Byte

    return Primitives.Unknown


def evaluate_operation(type_stack: List[Types], ops_stack: List[str], file: str, line: int):
    op = ops_stack.pop()

    # Binary operators
    if op in binary_operators:
        a = type_stack.pop()
        b = type_stack.pop()

        type_stack.append(apply_op_binary(a, b, op))

    # Uninary operators
    elif op in unary_operators:
        a = type_stack.pop()
        type_stack.append(apply_op_uinary(a, op))


def evaluate_stack(eval_stack: List[int | str],
                   types: List[Types],
                   file: str, line: int) -> tuple[List[int], List[Types]]:

    type_stack: List[Primitives] = []
    ops_stack: List[str] = []

    for i, token in enumerate(eval_stack[::-1]):
        i = len(eval_stack) - (i+1)

        if str(token) == "(":
            ops_stack.append(token)

        elif str(token) == ")":
            while len(ops_stack) > 0 and ops_stack[-1] != "(":
                evaluate_operation(type_stack, ops_stack, file, line)

            if len(ops_stack) > 0:
                ops_stack.pop()

        elif str(token) in operator_list:
            while len(ops_stack) > 0 and operator_predence(ops_stack[-1]) >= operator_predence(token):
                evaluate_operation(type_stack, ops_stack, file, line)

            ops_stack.append(token)

        else:
            type_stack.append(types[i])

    while len(ops_stack) > 0:
        evaluate_operation(type_stack, ops_stack, file, line)

    if len(type_stack) != 1:
        print(f"{file}:{line}:")
        print(
            f"Typecheck Error : unable to type evaluate following stack {eval_stack}")
        exit(1)
    return [0], type_stack


def typecheck_program(program: Program):
    type_stack: List[Types] = []
    value_stack: List[int | str] = []

    assert  len(OpType) == 9, "Exhaustive handling of operations"

    for op in program.operations:

        if op.type == OpType.OpBeginScope:
            pass

        elif op.type == OpType.OpEndScope:
            pass

        elif op.type == OpType.OpPush:
            value_stack = []
            type_stack = []
            for i, opr in enumerate(op.oprands[::-1]):
                val = opr
                tp = op.types[len(op.oprands) - (i+1)]

                value_stack.append(val)
                type_stack.append(tp)

        elif op.type == OpType.OpMov:
            deref = op.oprands[-2]
            tp = op.types[-1]

            if deref:
                tp = Primitives.Byte

            if len(type_stack) == 0:
                print(f"{op.file}:{op.line}:")
                print(f"Typecheck error: attempting to typecheck an empty typestack")
                exit(1)

            value_stack, type_stack = evaluate_stack(
                value_stack, type_stack, op.file, op.line)

            value_stack.pop()
            found = type_stack.pop()

            if tp != found:
                print(f"{op.file}:{op.line}:")
                print(
                    f"Typecheck error: mismatch type on assignment, expected `{type_str(tp)}` found `{type_str(found)}`")
                exit(1)

        elif op.type == OpType.OpIf:
            if len(type_stack) == 0:
                print(f"{op.file}:{op.line}:")
                print(f"Typecheck error: attempting to typecheck an empty typestack")
                exit(1)

            value_stack, type_stack = evaluate_stack(
                value_stack, type_stack, op.file, op.line)

            value_stack.pop()
            found = type_stack.pop()
            if found != Primitives.Bool:
                print(f"{op.file}:{op.line}:")
                print(
                    f"Typecheck error: unexpected type on if expression, expected `bool` found `{type_str(found)}")
                exit(1)

        elif op.type == OpType.OpElseIf:
            if len(type_stack) == 0:
                print(f"{op.file}:{op.line}:")
                print(f"Typecheck error: attempting to typecheck an empty typestack")
                exit(1)

            value_stack, type_stack = evaluate_stack(
                value_stack, type_stack, op.file, op.line)

            value_stack.pop()
            found = type_stack.pop()
            if found != Primitives.Bool:
                print(f"{op.file}:{op.line}:")
                print(
                    f"Typecheck error: unexpected type on else if expression, expected `bool` found `{type_str(found)}`")
                exit(1)

        elif op.type == OpType.OpElse:
            pass

        elif op.type == OpType.OpWhile:
            if len(type_stack) == 0:
                print(f"{op.file}:{op.line}:")
                print(f"Typecheck error: attempting to typecheck an empty typestack")
                exit(1)

            value_stack, type_stack = evaluate_stack(
                value_stack, type_stack, op.file, op.line)

            value_stack.pop()
            found = type_stack.pop()
            if found != Primitives.Bool:
                print(f"{op.file}:{op.line}:")
                print(
                    f"Typecheck error: unexpected type on while expression, expected `bool` found `{type_str(found)}")
                exit(1)

        elif op.type == OpType.OpPrint:
            value_stack, type_stack = evaluate_stack(
                value_stack, type_stack, op.file, op.line)

            value_stack.pop()

            op.types.append(type_stack.pop())
        