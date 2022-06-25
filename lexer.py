
from dataclasses import dataclass
from pprint import pprint
import re
from typing import List, Tuple

from misc import report_error


@dataclass
class Token:
    word: str
    file: str
    line: int


def lex_source(file_path) -> List[Token]:
    tokens: List[Token] = []

    with open(file_path) as file:
        lines = re.split("[\n]", file.read())

        for line_num, line in enumerate(lines):

            line = line.split("//")[0].strip()
            line_num = line_num + 1

            # Skip empty lines
            if line == "":
                continue

            #  Matching Declaration
            elif re.fullmatch("[a-zA-Z0-9_]+\s*:\^?[a-zA-Z0-9]+", line):
                lside_tks = re.split(":", line)
                tokens.append(Token(lside_tks[0].strip(), file_path, line_num))

                if len(lside_tks) == 2:
                    tokens.append(
                        Token(":", file_path, line_num))
                    tokens.append(
                        Token(lside_tks[1].strip(), file_path, line_num))

            #  Matching Assignments
            elif re.fullmatch("\^?[a-zA-Z0-9_]+\s*:?(\^?[a-zA-Z0-9]+)?\s*=.*", line):
                tks = re.split("=", line)

                if len(tks) != 2:
                    report_error(
                        f"asssignment must be of form var=expression", file_path, line_num)

                lside = tks[0].strip()
                rside = tks[1].strip()

                lside_tks = re.split(":", lside)
                tokens.append(Token(lside_tks[0].strip(), file_path, line_num))

                if len(lside_tks) == 2:
                    tokens.append(
                        Token(":", file_path, line_num))
                    if lside_tks[1].strip() != "":
                        tokens.append(
                            Token(lside_tks[1].strip(), file_path, line_num))

                tokens.append(Token("=", file_path, line_num))

                # Matching functions
                if re.fullmatch("func\s*\(([a-zA-Z0-9,:\s]*)\)\s*(?:->)?\s*\(?([a-zA-Z0-9,\s]*)\)?\s*{", rside):
                    tks = re.findall("func\s*\(([a-zA-Z0-9,:\s]*)\)\s*(?:->)?\s*\(?([a-zA-Z0-9,\s]*)\)?\s*{", line).pop()

                    tokens.append(Token("func", file_path, line_num))
                    tokens += [Token(tk.strip(), file_path, line_num) for tk in tks]
                    tokens.append(Token("{", file_path, line_num))
                else:
                    tokens.append(Token(rside, file_path, line_num))

            # Matching if keyword
            elif re.fullmatch("if .*{", line):
                tks = re.findall("if (.*){", line)
                tokens.append(Token("if", file_path, line_num))
                tokens.append(Token(tks.pop().strip(), file_path, line_num))
                tokens.append(Token("{", file_path, line_num))

            # Matching elif keyword
            elif re.fullmatch("else\s*if .*{", line):
                tks = re.findall("else[ ]*if (.*){", line)
                tokens.append(Token("else", file_path, line_num))
                tokens.append(Token("if", file_path, line_num))
                tokens.append(Token(tks.pop().strip(), file_path, line_num))
                tokens.append(Token("{", file_path, line_num))

            # Matching else keyword
            elif re.fullmatch("else\s*{", line):
                tokens.append(Token("else", file_path, line_num))
                tokens.append(Token("{", file_path, line_num))

            # Matching while keyword
            elif re.fullmatch("while .*{", line):
                tks = re.findall("while (.*){", line)
                tokens.append(Token("while", file_path, line_num))
                tokens.append(Token(tks.pop().strip(), file_path, line_num))
                tokens.append(Token("{", file_path, line_num))

            # Matching end of blocks
            elif re.fullmatch("}", line):
                tokens.append(Token("}", file_path, line_num))

            # elif re.fullmatch("[a-zA-Z][a-zA-Z0-9_]*[ ]*::")

            # Match return statement
            elif re.fullmatch("->.*", line):
                tks = re.findall("->(.*)", line)

                tokens.append(Token("->", file_path, line_num))
                tokens.append(Token(tks.pop().strip(), file_path, line_num))

            # Matching print intrinsic
            elif re.fullmatch("print .+", line):
                tks = re.findall("print (.+)", line)
                tokens.append(Token("print", file_path, line_num))
                tokens.append(Token(tks.pop().strip(), file_path, line_num))

            # Other
            else:
                report_error(f"unexpected token `{line}`", file_path, line_num)

    # pprint([token.word for token in tokens])
    return tokens
