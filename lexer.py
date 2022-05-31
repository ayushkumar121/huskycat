# from dataclasses import dataclass
# from enum import Enum
# import re
# from typing import List
# from unicodedata import numeric


# class TokenType(Enum):
#     Keyword = 0
#     Intedifier = 1
#     Constant = 2
#     Operator = 3
#     Symbol = 4
#     Expression = 5

# class Operators(Enum):
#     Declaration = 0
#     Assignment = 1
#     DeclarationAssignment = 2


# @dataclass
# class Token:
#     typ: TokenType
#     word: str
#     value: int
#     file: str
#     line: int
#     col: int

# operators_map = {
#     ":=": Operators.DeclarationAssignment,
#     ":": Operators.Declaration,
#     "=": Operators.Assignment,
# }


# def lex(file_name: str) -> List[Token]:
#     file = open(file=file_name)
#     contents = file.read()

#     tokens = []

#     for line in re.split("[;]", contents):
#         line = line.strip()

#         if not line:
#             continue

#         for operator in operators_map.keys():
#             if line.__contains__(operator):
#                 words = line.split(operator)
#                 for word in words:
#                     tokens.append(Token(TokenType.Expression,
#                                         word.strip(), 0, file_name, 0, 0))

#                     if word != words[-1]:  # check if the last word
#                         tokens.append(Token(TokenType.Operator,
#                                             operator, operators_map[operator], file_name, 0, 0))

#         if line.__contains__("{"):
#             words = line.split("{")
#             for word in words:
#                 tokens.append(Token(TokenType.Expression,
#                                     word.strip(), 0, file_name, 0, 0))

#                 if word != words[-1]:  # check if the last word
#                     tokens.append(Token(TokenType.Expression,
#                                   "{", 0, file_name, 0, 0))
#         else:
#             tokens.append(Token(TokenType.Expression,
#                           line, 0, file_name, 0, 0))

#         # for word in re.split("[\t ()]", line.split("#")[0]):
#         #     word = word.strip()
#         #     if word != "":
#         #         if matching_string:
#         #             tokens[-1].word += " " + word

#         #             # Strings ending
#         #             if word.endswith("\""):
#         #                 matching_string = False
#         #         else:
#         #             # Checking Keywords
#         #             if keywords_map.keys().__contains__(word):
#         #                 tokens.append(Token(TokenType.Keyword, word,
#         #                               keywords_map[word], file_name, 0, 0))

#         #             # Checking Operators
#         #             elif operators_map.keys().__contains__(word):
#         #                 tokens.append(Token(TokenType.Operator, word,
#         #                               operators_map[word], file_name, 0, 0))
#         #             # Strings starts
#         #             elif word.startswith("\""):
#         #                 matching_string = True
#         #                 tokens.append(Token(TokenType.Constant,
#         #                               word, Contants.String, file_name, 0, 0))

#         #             # Match expressions
#         #             elif re.match("[0-9].*", word):
#         #                 tokens.append(Token(TokenType.Expression,
#         #                               word, Contants.Decimal, file_name, 0, 0))

#         #             else:
#         #                 tokens.append(
#         #                     Token(TokenType.Intedifier, word, 0, file_name, 0, 0))

#     return tokens
