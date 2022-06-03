from ctypes import c_char
from dataclasses import dataclass
from parser import Program


@dataclass
class Symbol:
    name: str


def compiler_program(program: Program) -> str:

    # TODO: make the source code statically linked

    c_code = """
# include<stdio.h>

typedef long long int i64;

typedef struct{
int len;
char *data;
} Str;

int main() {
"""
    

    c_code += "}"

    return c_code
