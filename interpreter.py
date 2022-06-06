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
    if primitive in [Primitives.I32, Primitives.F32]:
        return 4
    elif primitive in [Primitives.I64, Primitives.F64, Primitives.Ptr]:
        return 8
    elif primitive in [Primitives.Bool, Primitives.Byte]:
        return 1

    return 8


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
                return len(scopes) - (i + 1), len(scope) - (j+1)

    return -1, -1


def interpret_program(program: Program):
    value_stack: List[int | str] = []
    scopes: List[List[Var]] = []

    ip = 0
    while ip < len(program.operations):
        op = program.operations[ip]

        if op.type == OpType.OpBeginScope:
            vars = []
            for opi, opr in enumerate(op.oprands[::-1]):
                var = opr
                tp = op.types[opi]

                vars.append(Var(var, tp, size_of(
                    tp), bytearray(size_of(tp))))

            scopes.append(vars)
            ip += 1

        elif op.type == OpType.OpEndScope:
            scopes.pop()

            if len(op.oprands) > 0:
                ip = op.oprands[-1]
            else:
                ip += 1

        elif op.type == OpType.OpPush:
            for opr in op.oprands[::-1]:
                i, j = find_var_scope(opr, scopes)
                if i != -1:
                    val = int.from_bytes(
                        scopes[i][j].value, "big")
                    value_stack.append(val)
                else:
                    value_stack.append(opr)

            ip += 1

        elif op.type == OpType.OpMov:
            var = op.oprands[-1]
            tp = op.types[-1]

            value_stack = evaluate_stack(
                value_stack, op.file, op.line)
            i, j = find_var_scope(var, scopes)

            if i != -1:
                scopes[i][j].value = int(value_stack.pop()).to_bytes(
                    size_of(tp), "big")
            else:
                print(f"{op.file}:{op.line}:")
                print(
                    f"Interpreter Error : incorrect variable index for {var}")
                exit(1)

            ip += 1

        elif op.type == OpType.OpIf:
            tj = op.oprands[-1]
            value_stack = evaluate_stack(
                value_stack, op.file, op.line)

            if value_stack.pop() < 1:
                ip += tj + 2
            else:
                ip += 1

        elif op.type == OpType.OpWhile:
            tj = op.oprands[-1]
            value_stack = evaluate_stack(
                value_stack, op.file, op.line)

            if value_stack.pop() < 1:
                ip += tj + 2
            else:
                ip += 1

        elif op.type == OpType.OpPrint:
            val_or_var = op.oprands[-1]
            tp = op.types[-1]

            i, j = find_var_scope(val_or_var, scopes)
            val = val_or_var

            if i != -1:
                val = int.from_bytes(
                    scopes[i][j].value, "big")

            if tp in [Primitives.I32, Primitives.I64, Primitives.F32, Primitives.F64]:
                print(val, end="")
            elif tp == Primitives.Byte:
                print(chr(val), end="")
            elif tp == Primitives.Bool:
                print("true" if val == 1 else "false", end="")
            elif tp == Primitives.Ptr:
                print(f"^{val}", end="")
            else:
                print(f"{op.file}:{op.line}:")
                print(
                    f"Interpreter Error : undefined print for this type")
                exit(1)                

            ip += 1
