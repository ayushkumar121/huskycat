#!/usr/bin/python3

from dataclasses import dataclass
from enum import Enum
import re

import pprint

import lexer


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
    value: int
    file: str
    line: int
    col: int


symbol_table = {}

for line in re.split("[\n]", contents):
    line = line.strip()

    # Matching expressions
    if re.match("[a-zA-Z0-9]+[ ]*=[ ]*[a-zA-Z0-9+\-/%\"]+", line):
        tokens = re.split("[ ]*=[ ]*", line)

        if len(tokens) > 2:
            print("Parsing Error : muliple '=' found on right side of the argument")
            exit(1)

        left_side = tokens[0]
        right_side = tokens[1]

        # Evaluate `right_side`
        if re.fullmatch("[0-9]+", right_side):
            
            val = int(right_side)
            symbol_table[left_side] = Symbol(
                left_side, DataType.Int, val, __file__, 0, 0)

        elif re.fullmatch("\".*\"", right_side):
            symbol_table[left_side] = Symbol(
                left_side, DataType.Str, right_side, __file__, 0, 0)

pprint.pprint(symbol_table)

# tokens = lexer.lex("basic.hc")

# for token in tokens:
#     print(token.word, "->", token.typ)
#     print()
