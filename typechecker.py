from typing import List
from misc import not_implemented
from parser import OpType, Primitives, Program


def predence(operator: str) -> int:
    if operator in ["+", "-", "||", "&&"]:
        return 1
    if operator in ["*", "/", "<", ">"]:
        return 2
    if operator in "!":
        return 3
    return 0


def apply_op_binary(a: Primitives, b: Primitives, op: str) -> Primitives:
    if op in ["+",  "-", "*", "/"]:
        return a
    elif op == "%":
        return Primitives.I64
    elif op in ["||", "&&", ">", "<"]:
        return Primitives.Bool

    return Primitives.Unknown


def apply_op_uinary(a: int, op: str) -> Primitives:
    if op == "!":
        return Primitives.Bool
    elif op == "^":
        return Primitives.Byte

    return Primitives.Unknown


def evaluate_stack(eval_stack: List[int | str],
                   types: List[Primitives],
                   file: str, line: int) -> tuple[List[int], List[Primitives]]:

    type_stack = []
    ops_stack = []

    for i, token in enumerate(eval_stack):
        if str(token) == "(":
            ops_stack.append(token)

        elif str(token) == ")":
            while len(ops_stack) > 0 and ops_stack[-1] != "(":
                a = type_stack.pop()
                b = type_stack.pop()

                op = ops_stack.pop()

                type_stack.append(apply_op_binary(a, b, op))

            while len(ops_stack) > 0:
                ops_stack.pop()

        elif token in ["+", "-", "/", "*", "%", "<", ">", "&&", "||", "!", "^"]:
            while len(ops_stack) > 0 and predence(ops_stack[-1]) >= predence(token):
                op = ops_stack.pop()

                # Binary operators
                if op in ["+", "-", "/", "*", "%", "<", ">", "&&", "||"]:
                    a = type_stack.pop()
                    b = type_stack.pop()

                    type_stack.append(apply_op_binary(a, b, op))

                # Uninary operators
                elif op in ["!", "^"]:
                    a = type_stack.pop()
                    type_stack.append(apply_op_uinary(a, op))

            ops_stack.append(token)

        else:
            type_stack.append(types[i])

    while len(ops_stack) > 0:
        op = ops_stack.pop()

        # Binary operators
        if op in ["+", "-", "/", "*", "%", "<", ">", "&&", "||"]:
            a = type_stack.pop()
            b = type_stack.pop()

            type_stack.append(apply_op_binary(a, b, op))

        # Uninary operators
        elif op in ["!", "^"]:
            a = type_stack.pop()
            type_stack.append(apply_op_uinary(a, op))

    return [0], type_stack


def typecheck_program(program: Program):
    type_stack: List[Primitives] = []
    value_stack: List[int | str] = []

    for op in program.operations:

        if op.type == OpType.OpBeginScope:
            pass

        elif op.type == OpType.OpEndScope:
            pass

        elif op.type == OpType.OpPush:
            n = len(op.oprands)
            for i, opr in enumerate(op.oprands[::-1]):
                val = opr
                tp = op.types[n - (i + 1)]

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
                    f"Typecheck error: mismatch type on assignment, expected {tp} found {found}")
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
                    f"Typecheck error: unexpected type on if expression, expected {Primitives.Bool}")
                exit(1)

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
                    f"Typecheck error: unexpected type on while expression, expected {Primitives.Bool}")
                exit(1)

        elif op.type == OpType.OpPrint:
            value_stack, type_stack = evaluate_stack(
                value_stack, type_stack, op.file, op.line)

            value_stack.pop()

            op.types.append(type_stack.pop())
