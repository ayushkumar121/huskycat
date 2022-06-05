from dataclasses import dataclass
from typing import List, Type
from misc import not_implemented
from parser import OpType, Primitives, Program


@dataclass
class Var:
    name: str
    type: Primitives
    size: int
    value: bytearray


def size_of(primitive: Primitives) -> int:
    if primitive == Primitives.I32:
        return 4
    elif primitive == Primitives.I64:
        return 8
    elif primitive == Primitives.F32:
        return 4
    elif primitive == Primitives.F64:
        return 8
    elif primitive == Primitives.Bool:
        return 1

    return 0


def predence(operator: str) -> int:
    if operator in ["+", "-", "||", "&&"]:
        return 1
    if operator in ["*", "/", "<", ">"]:
        return 2
    if operator in "!":
        return 3
    return 0


def apply_op_binary(a: int, b: int, op: str) -> int:
    if op == "+":
        return a + b
    elif op == "-":
        return a-b
    elif op == "/":
        return a / b
    elif op == "*":
        return a * b
    elif op == "%":
        return a % b
    elif op == "||":
        return 1 if (a or b) else 0
    elif op == "&&":
        return 1 if (a and b) else 0
    elif op == "<":
        return 1 if (a < b) else 0
    elif op == ">":
        return 1 if (a > b) else 0
    return 0


def apply_op_uinary(a: int, op: str) -> int:
    if op == "!":
        return 1 if (not a) else 0
    return 0


def evaluate_stack(eval_stack: List[int | str], file: str, line: int) -> tuple[List[int]]:
    value_stack = []
    ops_stack = []

    for token in eval_stack:
        if str(token) == "(":
            ops_stack.append(token)

        elif str(token) == ")":
            while len(ops_stack) > 0 and ops_stack[-1] != "(":
                a = value_stack.pop()
                b = value_stack.pop()

                op = ops_stack.pop()

                value_stack.append(apply_op_binary(a, b, op))

            while len(ops_stack) > 0:
                ops_stack.pop()

        elif token in ["+", "-", "/", "*", "%", "<", ">", "&&", "||", "!"]:
            while len(ops_stack) > 0 and predence(ops_stack[-1]) >= predence(token):
                op = ops_stack.pop()

                # Binary operators
                if op in ["+", "-", "/", "*", "%", "<", ">", "&&", "||"]:
                    a = value_stack.pop()
                    b = value_stack.pop()

                    value_stack.append(apply_op_binary(a, b, op))

                # Uninary operators
                elif op in "!":
                    a = value_stack.pop()
                    value_stack.append(apply_op_uinary(a, op))

            ops_stack.append(token)

        else:
            value_stack.append(token)

    while len(ops_stack) > 0:
        op = ops_stack.pop()

        # Binary operators
        if op in ["+", "-", "/", "*", "%", "<", ">", "&&", "||"]:
            a = value_stack.pop()
            b = value_stack.pop()

            value_stack.append(apply_op_binary(a, b, op))

        # Uninary operators
        elif op in "!":
            a = value_stack.pop()
            value_stack.append(apply_op_uinary(a, op))

    return value_stack


def find_var_scope(var: str, scopes: List[List[Var]]) -> tuple[int, int]:
    for i, scope in enumerate(scopes[::-1]):
        for j, v in enumerate(scope[::-1]):
            if v.name == var:
                return i, j

    return -1, -1


def interpret_program(program: Program):
    value_stack: List[int | str] = []

    scopes: List[List[Var]] = []

    ip = 0
    while ip < len(program.operations):
        op = program.operations[ip]

        if op.type == OpType.OpBeginScope:
            vars = []
            while len(op.oprands) > 0:
                var = op.oprands.pop()
                type = op.types.pop()

                vars.append(Var(var, type, size_of(
                    type), bytearray(size_of(type))))

            scopes.append(vars)
            ip += 1

        elif op.type == OpType.OpEndScope:
            scopes.pop()
            ip += 1

        elif op.type == OpType.OpPush:
            while len(op.oprands) > 0:
                val_or_var = op.oprands.pop()
                op.types.pop()

                i, j = find_var_scope(val_or_var, scopes)
                if i != -1:
                    value_stack.append(int.from_bytes(
                        scopes[i][j].value, "big"))
                else:
                    value_stack.append(val_or_var)

            ip += 1

        elif op.type == OpType.OpMov:
            var = op.oprands.pop()

            value_stack = evaluate_stack(
                value_stack, op.file, op.line)
            i, j = find_var_scope(var, scopes)

            if i != -1:
                scopes[i][j].value = int(value_stack.pop()).to_bytes(
                    4, "big", signed=True)
            else:
                print(f"{op.file}:{op.line}:")
                print(
                    f"Interpreter Error : internal interpreter error (incorrect variable index)")
                exit(1)

            ip += 1

        elif op.type == OpType.OpIf:
            tj = op.oprands.pop()
            value_stack = evaluate_stack(
                value_stack, op.file, op.line)

            if value_stack.pop()  < 1:
                ip += tj + 2
            else:
                ip += 1

        elif op.type == OpType.OpPrint:
            for i, val_or_var in enumerate(op.oprands):
                type = op.types[i]

                i, j = find_var_scope(val_or_var, scopes)
                val = val_or_var

                if i != -1:
                    val = int.from_bytes(
                        scopes[i][j].value, "big", signed=True)

                if type in [Primitives.I32, Primitives.I64, Primitives.F32, Primitives.F64]:
                    print(val, end=" ")
                elif type == Primitives.Bool:
                    print("true" if val == 1 else "false", end=" ")

            print()
            ip += 1
