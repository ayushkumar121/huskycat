from dataclasses import dataclass
from typing import List
from parser import DataType, OpType, Program


@dataclass
class Symbol:
    name: str
    value: int


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

    return int(value_stack[0])


def interpret_program(program: Program):
    symbol_table = {}

    for op in program.operations:
        # Handling string literals
        if op.type == OpType.OpVarAssign and op.data_type == DataType.Str:
            left_side = op.name
            right_side = op.value

            symbol_table[left_side] = Symbol(
                left_side, right_side)
        # Handling a mathetical expression
        elif op.type == OpType.OpVarAssign and op.data_type == DataType.Int:

            left_side = op.name
            right_side = op.value

            i = 1

            eval_stack = []
            num_literal = 0
            var_name = ""

            evaluating_literal = False
            evaluating_variable = False

            right_side = "$" + right_side

            for ch in right_side[::-1]:
                if ch.isdigit() and not evaluating_variable:
                    num_literal = num_literal + int(ch) * i
                    i = i * 10
                    evaluating_literal = True
                elif ch.isalpha():
                    if evaluating_literal:
                        var_name = ch + str(num_literal)
                    else:
                        var_name = ch + var_name

                    evaluating_literal = False
                    evaluating_variable = True
                elif ch in "+-/*%()":
                    if evaluating_literal:
                        eval_stack.append(num_literal)
                    elif evaluating_variable:
                        if var_name in symbol_table.keys():
                            eval_stack.append(symbol_table[var_name].value)
                        else:
                            print(
                                f"{op.file_path}:{op.line_num}:")
                            print(
                                f"Interpretation Error : unrecognised symbol varible `{var_name}` during eval")
                            exit(1)

                    i = 1
                    num_literal = 0
                    var_name = ""

                    evaluating_literal = False
                    evaluating_variable = False

                    eval_stack.append(ch)
                elif ch == "$":
                    if evaluating_literal:
                        eval_stack.append(num_literal)
                    elif evaluating_variable:
                        if var_name in symbol_table.keys():
                            eval_stack.append(symbol_table[var_name].value)
                        else:
                            print(
                                f"Interpretation Error : unrecognised symbol varible `{var_name}` during eval")
                            exit(1)

                    i = 1
                    num_literal = 0
                    var_name = ""

                    evaluating_literal = False
                    evaluating_variable = False
                elif ch == " ":
                    pass
                else:
                    print(
                        f"Interpretation Error : unrecognised symbol {ch} during eval")
                    exit(1)

            val = evaluate_stack(eval_stack)
            symbol_table[left_side] = Symbol(
                left_side, val)
        elif op.type == OpType.OpPrintVar:
            if op.name in symbol_table.keys():
                print(symbol_table[op.name].value)
            else:
                print(f"{op.file_path}:{op.line_num}:")
                print(
                    f"Interpretation Error : cannot print unknown symbol `{op.name}`")
                exit(1)
