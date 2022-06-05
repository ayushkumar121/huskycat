from pprint import pprint
from typing import List
from parser import OpType, Primitives, Program


def compile_program_partial(program: Program) -> str:
    c_code = ""

    type_stack: List[Primitives] = []
    value_stack: List[int | str] = []

    for op in program.operations:

        if op.type == OpType.OpBeginScope:
            c_code += "{\n"

            while len(op.oprands) > 0:
                var = op.oprands.pop()
                type = op.types.pop()

                if type == Primitives.I32:
                    c_code += f"i32 {var};\n"
                elif type == Primitives.I64:
                    c_code += f"i64 {var};\n"
                elif type == Primitives.F32:
                    c_code += f"f32 {var};\n"
                elif type == Primitives.F64:
                    c_code += f"f64 {var};\n"
                elif type == Primitives.Bool:
                    c_code += f"bool {var};\n"
                else:
                    print(f"{op.file}:{op.line}:")
                    print(
                        f"Compiler Error : type not defined for compilation")
                    exit(1)

        elif op.type == OpType.OpEndScope:
            c_code += "}\n"

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

        elif op.type == OpType.OpIf:
            c_code += "if("
            while len(value_stack) > 0:
                val = value_stack.pop()
                type = type_stack.pop()

                c_code += f"{val}"
            c_code += ")"

        elif op.type == OpType.OpWhile:
            c_code += "while("
            while len(value_stack) > 0:
                val = value_stack.pop()
                type = type_stack.pop()

                c_code += f"{val}"
            c_code += ")"

        elif op.type == OpType.OpPrint:
            for i, val_or_var in enumerate(op.oprands):
                type = op.types[i]

                # different print for different type
                if type == Primitives.I32:
                    c_code += f"print_i32({val_or_var});\n"
                elif type == Primitives.I64:
                    c_code += f"print_i64({val_or_var});\n"
                elif type == Primitives.F32:
                    c_code += f"print_f32({val_or_var});\n"
                elif type == Primitives.F64:
                    c_code += f"print_f64({val_or_var});\n"
                elif type == Primitives.Bool:
                    c_code += f"print_bool({val_or_var});\n"
                else:
                    print(f"{op.file}:{op.line}:")
                    print(
                        f"Compiler Error : print is not defined for following type")
                    exit(1)

            c_code += f"printf(\"\\n\");\n"

    return c_code


def compile_program(program: Program) -> str:

    c_code = """
# include<stdio.h>

typedef int i32;
typedef long long i64;

typedef float f32;
typedef double f64;

typedef unsigned char bool;

typedef struct{
int len;
char *data;
} Str;

void print_i32(i32 a) {printf(\"%d \", a);}
void print_i64(i64 a) {printf(\"%lld \", a);}

void print_f32(f32 a) {printf(\"%f \", a);}
void print_f64(f64 a) {printf(\"%lf \", a);}

void print_bool(bool a) {printf(\"%s \", a?"true":"false");}

int main() {
"""
    c_code += compile_program_partial(program)
    c_code += """return 0;
}
"""

    return c_code
