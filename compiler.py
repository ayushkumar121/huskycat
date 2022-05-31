from dataclasses import dataclass
from parser import OpType, Program


def compiler_program(program: Program) -> str:
    symbols = []

    # TODO: make the source code statically linked

    c_code = "#include<stdio.h>\n"
    c_code += "int main() { \n"

    for op in program.operations:
        if op.type == OpType.OpVarAssign:
            if op.name not in symbols:
                c_code += f"int {op.name}={op.value};\n"
                symbols.append(op.name)
            else:
                c_code += f"{op.name}={op.value};\n"
        elif op.type == OpType.OpPrintVar:
            c_code += f'printf("%d\\n",{op.name});\n'

    c_code += "}"

    return c_code
