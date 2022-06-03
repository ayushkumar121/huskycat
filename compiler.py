from ctypes import c_char
from dataclasses import dataclass
import enum
from time import time
from typing import List
from parser import OpType, Primitives, Program


@dataclass
class Symbol:
    name: str


def compiler_program(program: Program) -> str:

    type_stack: List[Primitives] = []
    value_stack: List[int | str] = []
    
    # TODO: make the source code statically linked

    c_code = """
# include<stdio.h>

typedef long long int i64;
typedef int bool;

typedef struct{
int len;
char *data;
} Str;

int main() {
"""
    for op in program.operations:

        if op.type == OpType.OpBeginScope:
            c_code += "{\n"

            while len(op.oprands) > 0:
                var = op.oprands.pop()
                type = op.types.pop()

                if type == Primitives.Int:
                    c_code += f"i64 {var};\n"
                elif type == Primitives.Bool:
                    c_code += f"bool {var};\n"
            
        elif op.type == OpType.OpEndScope:
            c_code += "}"

        elif op.type == OpType.OpPush:
            while len(op.oprands) > 0:
                val_or_var = op.oprands.pop()
                type = op.types.pop()

                value_stack.append(val_or_var)
                type_stack.append(type)

        elif op.type == OpType.OpMov:
            var = op.oprands.pop()
            type = op.types.pop()

            c_code += f"{var}="
            while len(value_stack) > 0:
                val = value_stack.pop()
                type = type_stack.pop()

                c_code += f"{val}"
            c_code += f";\n"

        elif op.type == OpType.OpPrint:
            for i, val_or_var in enumerate(op.oprands):
                type = op.types[i]

                # different print for different type
                if type ==  Primitives.Int:
                    c_code += f"printf(\"%lld\\n\", {val_or_var});\n"
                elif type ==  Primitives.Bool:
                    c_code += f"printf(\"%d\\n\", {val_or_var});\n"
    c_code += """
return 0;
}
"""

    return c_code
