
from dataclasses import dataclass
from enum import Enum, auto
import re
from typing import List


class DataType(Enum):
    Nil = auto()
    Int = auto()
    Str = auto()


class OpType(Enum):
    OpVarAssign = auto()
    OpPrintVar = auto()


@dataclass
class Operation:
    op_type: OpType
    name: str
    value: str
    data_type: DataType
    file_path: str
    line_num: int


@dataclass
class Program:
    operations: List[Operation]


def parse_program_from_file(file_path) -> Program:
    program = Program(operations=[])

    with open(file_path) as file:

        for line_num, line in enumerate(re.split("[\n]", file.read())):
            line = line.split("//")[0].strip()
            line_num = line_num + 1

            # Skip empty lines
            if line == "":
                pass

            # Matching string literal
            elif re.fullmatch("[a-zA-Z][a-zA-Z0-9_]*[ ]*=[ ]*\".*\"", line):
                tokens = re.split("[ ]*=[ ]*", line)

                if len(tokens) > 2:
                    print(f"{file_path}:{line_num}:")
                    print(
                        "Parsing Error: muliple '=' found on right side of the argument")
                    exit(1)

                left_side = tokens[0]
                right_side = tokens[1].removeprefix("\"").removesuffix("\"")

                program.operations.append(
                    Operation(OpType.OpVarAssign, left_side, right_side, DataType.Str, file_path, line_num))

            # Matching an int assignment
            elif re.fullmatch("[a-zA-Z][a-zA-Z0-9_]*[ ]*=[ ]*[a-zA-Z0-9+\-/%()]+", line):
                tokens = re.split("[ ]*=[ ]*", line)

                if len(tokens) > 2:
                    print(f"{file_path}:{line_num}:")
                    print(
                        "Parsing Error: muliple '=' found on right side of the argument")
                    exit(1)

                left_side = tokens[0]
                right_side = tokens[1]

                program.operations.append(
                    Operation(OpType.OpVarAssign, left_side, right_side, DataType.Nil, file_path, line_num))
            elif re.fullmatch("print[ ]*[a-zA-Z][a-zA-Z0-9_]*", line):
                tokens = re.split("[ ]+", line)

                if len(tokens) != 2:
                    print("Parsing Error : exactly one token is required after print")
                    exit(1)

                program.operations.append(
                    Operation(OpType.OpPrintVar, tokens[1], "", DataType.Nil, file_path, line_num))
            else:
                print(f"{file_path}:{line_num}:")
                print(f"Parsing Error: unexpected token `{line}`")
                exit(1)

    return program
