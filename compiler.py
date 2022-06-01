from dataclasses import dataclass
from parser import DataType, OpType, Program

@dataclass
class Symbol:
    name: str
    type: DataType

def compiler_program(program: Program) -> str:
    symbol_table = {}

    # TODO: make the source code statically linked

    c_code = """
#include<stdio.h>

typedef struct{
int len;
char *data;
} Str;

int main() {
"""

    for op in program.operations:
        if op.type == OpType.OpVarAssign and op.data_type == DataType.Str:
            
            if op.name not in symbol_table.keys():
                c_code += f"Str {op.name}={{.len={len(op.value)}, .data=\"{op.value}\"}};\n"
                symbol_table[op.name] = Symbol(op.name, DataType.Str)
            else:
                c_code += f"{op.name}={{.len={len(op.value)}, .data=\"{op.value}\"}};\n"
        
        elif op.type == OpType.OpVarAssign and op.data_type == DataType.Int:
            
            if op.name not in symbol_table.keys():
                c_code += f"int {op.name}={op.value};\n"
                symbol_table[op.name] = Symbol(op.name, DataType.Int)
            else:
                c_code += f"{op.name}={op.value};\n"

        elif op.type == OpType.OpPrintVar:

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
