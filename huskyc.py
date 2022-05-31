#!/usr/bin/python3

from dataclasses import dataclass
from enum import Enum
import re

import pprint
from typing import List

# import lexer


file = open(file="basic.hc")
contents = file.read()
file.close()


class DataType(Enum):
    Int = 0
    Str = 1


@dataclass
class Symbol:
    name: str
    type: DataType
    value: int | str
    file: str
    line: int
    col: int


symbol_table = {}


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


expressions = re.split("[\n]", contents)
for line in expressions:
    line = line.strip()

    # Matching expressions
    if re.match("[a-zA-Z][a-zA-Z0-9_]*[ ]*=[ ]*[a-zA-Z0-9+\-/%\"()]+", line):
        tokens = re.split("[ ]*=[ ]*", line)

        if len(tokens) > 2:
            print("Parsing Error : muliple '=' found on right side of the argument")
            exit(1)

        left_side = tokens[0]
        right_side = tokens[1]

        # Matching string literals
        if re.fullmatch("\".*\"", right_side):
            if (left_side not in symbol_table.keys()) or symbol_table[left_side].type == DataType.Str:
                symbol_table[left_side] = Symbol(
                    left_side, DataType.Str, right_side, __file__, 0, 0)
            else:
                print("Parsing Error : redefinition of variable not allowed")
                exit(1)

        # Evaluate `right_side`
        else:
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
                                f"Parsing Error : unrecognised symbol varible `{var_name}` during eval")
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
                                f"Parsing Error : unrecognised symbol varible `{var_name}` during eval")
                            exit(1)

                    i = 1
                    num_literal = 0
                    var_name = ""

                    evaluating_literal = False
                    evaluating_variable = False
                elif ch == " ":
                    pass
                else:
                    print("Parsing Error : unrecognised symbol during eval")
                    exit(1)

            val = evaluate_stack(eval_stack)

            if (left_side not in symbol_table.keys()) or symbol_table[left_side].type == DataType.Int:
                symbol_table[left_side] = Symbol(
                    left_side, DataType.Int, val, __file__, 0, 0)
            else:
                print("Parsing Error : redefinition of variable not allowed")
                exit(1)
    elif re.match("print[ ]*[a-zA-Z][a-zA-Z0-9_]*", line):
        tokens = re.split("[ ]+", line)
        
        if len(tokens) != 2:
            print("Parsing Error : exactly one token is required after print")
            exit(1)    

        variable_name = tokens[1]

        
        if variable_name in symbol_table.keys():
            print(symbol_table[variable_name].value)
        else:
            print(f"Parsing Error : cannot print unknown symbol `${variable_name}`")
            exit(1)

    else:
        # TODO: match every expression exhaustively
        pass
# pprint.pprint(symbol_table)

# tokens = lexer.lex("basic.hc")

# for token in tokens:
#     print(token.word, "->", token.typ)
#     print()
