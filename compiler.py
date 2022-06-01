from dataclasses import dataclass
import re
from parser import DataType, OpType, Program


@dataclass
class Symbol:
    name: str
    type: DataType


def compiler_program(program: Program) -> str:

    symbol_table = {}

    # TODO: make the source code statically linked

    c_code = """
# include<stdio.h>

typedef struct{
int len;
char *data;
} Str;

int main() {
"""

    for op in program.operations:
        if op.op_type == OpType.OpVarAssign and op.data_type == DataType.Str:

            if op.name not in symbol_table.keys():
                c_code += f"Str {op.name}={{.len={len(op.value)}, .data=\"{op.value}\"}};\n"
                symbol_table[op.name] = Symbol(op.name, DataType.Str)
            else:
                c_code += f"{op.name}={{.len={len(op.value)}, .data=\"{op.value}\"}};\n"

        elif op.op_type == OpType.OpVarAssign:
            operants = re.split("[+-/*%()]", op.value)
            assign_str = False

            for operant in operants:
                if operant == "":
                    pass

                elif operant[0].isalpha():
                    if operant in symbol_table.keys():
                        if symbol_table[operant].type == DataType.Str:
                            assign_str = True

                        if op.value in "+-/*%()":
                            print(f"{op.file_path}:{op.line_num}:")
                            print(
                                f"Compilation Error: string airethmatic is not allowed")
                            exit(1)

                    else:
                        print(f"{op.file_path}:{op.line_num}:")
                        print(f"Compilation Error: unknown variable {operant}")
                        exit(1)

            if op.name not in symbol_table.keys():
                if assign_str:
                    c_code += f"Str {op.name}={op.value};\n"
                    symbol_table[op.name] = Symbol(op.name, DataType.Str)
                else:
                    c_code += f"int {op.name}={op.value};\n"
                    symbol_table[op.name] = Symbol(op.name, DataType.Int)

            else:
                c_code += f"{op.name}={op.value};\n"

        elif op.op_type == OpType.OpPrintVar:

            if op.name in symbol_table.keys():
                if symbol_table[op.name].type == DataType.Int:
                    c_code += f"printf(\"%d\\n\", {op.name});\n"
                elif symbol_table[op.name].type == DataType.Str:
                    c_code += f"printf(\"%s\\n\", {op.name}.data);\n"
            else:
                print(f"{op.file_path}:{op.line_num}:")
                print(f"Compilation Error: unknown variable {op.name}")
                exit(1)

    c_code += "}"

    return c_code
