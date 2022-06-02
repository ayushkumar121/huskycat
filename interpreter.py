from ast import Str
from dataclasses import dataclass
from typing import List
from misc import not_implemented
from parser import OpType, Program

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


def evaluate_stack(eval_stack: List[int | str]) -> int:
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

    return value_stack[0]


def interpret_program(program: Program):
    type_stack = []
    value_stack = []
    symbol_stack = []

    for op in program.operations:

        if op.type == OpType.OpBeginScope:

            pass

        if op.type == OpType.OpEndScope:
            pass

        elif op.type == OpType.OpPush:
            pass

        elif op.type == OpType.OpMov:
            pass

        elif op.type == OpType.OpPrint:
            pass
    
    not_implemented()
