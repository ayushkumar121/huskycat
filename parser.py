
from dataclasses import dataclass
from enum import Enum, auto
import re
from typing import List


class OpType(Enum):
    OpVarAssign = auto()
    OpPrintVar = auto()


@dataclass
class Operation:
    type: OpType
    name: str
    value: str


@dataclass
class Program:
    operations: List[Operation]


def parse_program_from_file(file_path) -> Program:
    program = Program(operations=[])

    with open(file_path) as file:

        for line_num, line in enumerate(re.split("[\n]", file.read())):
            line = line.split("//")[0].strip()

            # Matching an assignment
            if re.fullmatch("[a-zA-Z][a-zA-Z0-9_]*[ ]*=[ ]*[a-zA-Z0-9+\-/%()]+", line):
                tokens = re.split("[ ]*=[ ]*", line)

                if len(tokens) > 2:
                    print(f"{file_path}:{line_num + 1}:")
                    print(
                        "Parsing Error: muliple '=' found on right side of the argument")
                    exit(1)

                left_side = tokens[0]
                right_side = tokens[1]
                program.operations.append(
                    Operation(OpType.OpVarAssign, left_side, right_side))
                pass
            elif re.fullmatch("print[ ]*[a-zA-Z][a-zA-Z0-9_]*", line):
                tokens = re.split("[ ]+", line)

                if len(tokens) != 2:
                    print("Parsing Error : exactly one token is required after print")
                    exit(1)

                program.operations.append(
                    Operation(OpType.OpPrintVar, tokens[1], ""))
            else:
                print(f"{file_path}:{line_num + 1}:")
                print("Parsing Error: unexpected token")
                exit(1)

    return program
