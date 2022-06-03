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
    if operator in "+-":
        return 1
    if operator in "*/":
        return 2
    return 0


def apply_op(a: int, b: int, op: str) -> int:
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

    return 0


def evaluate_stack(eval_stack: List[int | str],
                   type_stack: List[Primitives]) -> tuple[List[int | str], List[Primitives]]:
    value_stack = []
    ops_stack = []

    for ch in eval_stack:
        if str(ch) == ")":
            ops_stack.append(ch)
        elif str(ch) == "(":
            while len(ops_stack) > 0 and ops_stack[-1] != ")":
                a = value_stack.pop()
                b = value_stack.pop()

                op = ops_stack.pop()

                value_stack.append(apply_op(a, b, op))
            ops_stack.pop()
        elif str(ch) in "+-/*%":
            ops_stack.append(ch)
        else:
            value_stack.append(ch)

    while len(ops_stack) > 0:
        a = value_stack.pop()
        b = value_stack.pop()

        op = ops_stack.pop()

        value_stack.append(apply_op(a, b, op))

    return value_stack, [Primitives.I64]


def find_var_scope(var: str, scopes: List[List[Var]]) -> tuple[int, int]:
    for i, scope in enumerate(scopes[::-1]):
        for j, v in enumerate(scope[::-1]):
            if v.name == var:
                return i, j

    return -1, -1


def interpret_program(program: Program):
    type_stack: List[Primitives] = []
    value_stack: List[int | str] = []

    scopes: List[List[Var]] = []

    for op in program.operations:

        if op.type == OpType.OpBeginScope:
            vars = []
            while len(op.oprands) > 0:
                var = op.oprands.pop()
                type = op.types.pop()

                vars.append(Var(var, type, size_of(
                    type), bytearray(size_of(type))))

            scopes.append(vars)

        elif op.type == OpType.OpEndScope:
            scopes.pop()

        elif op.type == OpType.OpPush:
            while len(op.oprands) > 0:
                val_or_var = op.oprands.pop()
                type = op.types.pop()

                i, j = find_var_scope(val_or_var, scopes)
                if i != -1:
                    value_stack.append(int.from_bytes(
                        scopes[i][j].value, "big"))
                else:
                    value_stack.append(val_or_var)

                type_stack.append(type)

        elif op.type == OpType.OpMov:
            var = op.oprands.pop()
            type = op.types.pop()

            value_stack, type_stack = evaluate_stack(value_stack, type_stack)
            i, j = find_var_scope(var, scopes)

            if i != -1:
                scopes[i][j].value = int(value_stack.pop()).to_bytes(
                    4, "big", signed=True)
            else:
                print(f"{op.file}:{op.line}:")
                print(
                    f"Interpreter Error : error evaluating expression")
                exit(1)

        elif op.type == OpType.OpPrint:
            for i, val_or_var in enumerate(op.oprands):
                type = op.types[i]

                i, j = find_var_scope(val_or_var, scopes)
                val = val_or_var

                if i != -1:
                    val = int.from_bytes(
                        scopes[i][j].value, "big", signed=True)

                if type == Primitives.I64:
                    print(val)
                elif type == Primitives.Bool:
                    print("true" if val == 1 else "false")
