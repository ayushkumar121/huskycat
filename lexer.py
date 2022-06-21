
from dataclasses import dataclass
import re
from typing import List


@dataclass
class Token:
    word: str
    file: str
    line: int


def lex_source(file_path) -> List[Token]:
    tokens:List[Token] = []

    with open(file_path) as file:
        lines = re.split("[\n]", file.read())

        for line_num, line in enumerate(lines):

            line = line.split("//")[0].strip()
            line_num = line_num + 1

            # Skip empty lines
            if line == "":
                continue

            #  Matching Declaration
            elif re.fullmatch("[a-zA-Z][a-zA-Z0-9_]*:\^?[a-zA-Z][a-zA-Z0-9]*", line):
                pass
            #  Matching Assignments
            elif re.fullmatch("\^?[a-zA-Z][a-zA-Z0-9_]*:?\^?[a-zA-Z]?[a-zA-Z0-9]*?[ ]*=.*", line):
                pass

            # Matching if keyword
            elif re.fullmatch("if .*{", line):
                pass

            # Matching elif keyword
            elif re.fullmatch("else if .*{", line):
                pass

            # Matching else keyword
            elif re.fullmatch("else.*{", line):
                pass

            # Matching while keyword
            elif re.fullmatch("while .*{", line):
                pass

            # Matching end of blocks
            elif re.fullmatch("}", line):
               pass

            # Matching print intrinsic
            elif re.fullmatch("print .+", line):
                pass

            # Other
            else:
                print(f"{file_path}:{line_num}:")
                print(f"Lexing Error: unexpected token `{line}`")
                exit(1)

    return tokens
