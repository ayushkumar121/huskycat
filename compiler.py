from pprint import pprint
from typing import List
from parser import OpType, Primitives, Program

# def substitute_symbols(a:str) -> str:
#     if a == "^":
#         return "global_memory+"
#     return a


def compile_expression(value_stack: List, type_stack: List) -> str:
    c_code = ""
    brackets_start = False

    while len(value_stack) > 0:

        val = value_stack.pop()
        _ = type_stack.pop()

        if val == "^":
            c_code += f"*(global_memory+"
            brackets_start = True
        else:
            c_code += f"{val}"

            if brackets_start:
                c_code += f")"
                brackets_start = False

    return c_code


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
                elif type == Primitives.Byte:
                    c_code += f"byte {var};\n"
                elif type == Primitives.Ptr:
                    c_code += f"ptr {var};\n"
                else:
                    print(f"{op.file}:{op.line}:")
                    print(
                        f"Compiler Error : type not defined for compilation")
                    exit(1)

        elif op.type == OpType.OpEndScope:
            c_code += "}\n"

        elif op.type == OpType.OpPush:
            n = len(op.oprands)
            for i, opr in enumerate(op.oprands[::-1]):
                val_or_var = opr
                tp = op.types[n - (i + 1)]

                value_stack.append(val_or_var)
                type_stack.append(tp)

        elif op.type == OpType.OpMov:
            var = op.oprands[-1]
            deref = op.oprands[-2]
            tp = op.types[-1]

            if deref:
                c_code += f"global_memory[{var}]="
            else:
                c_code += f"{var}="

            c_code += compile_expression(value_stack, type_stack)
            c_code += f";\n"

        elif op.type == OpType.OpIf:
            c_code += "if("
            c_code += compile_expression(value_stack, type_stack)
            c_code += ")"

        elif op.type == OpType.OpWhile:
            c_code += "while("
            c_code += compile_expression(value_stack, type_stack)
            c_code += ")"

        elif op.type == OpType.OpPrint:
            tp = op.types[-1]

            # different print for different type
            if tp == Primitives.I32:
                c_code += f"print_i32("
            elif tp == Primitives.I64:
                c_code += f"print_i64("
            elif tp == Primitives.F32:
                c_code += f"print_f32("
            elif tp == Primitives.F64:
                c_code += f"print_f64("
            elif tp == Primitives.Bool:
                c_code += f"print_bool("
            elif tp == Primitives.Byte:
                c_code += f"print_byte("
            elif tp == Primitives.Ptr:
                c_code += f"print_ptr("
            else:
                print(f"{op.file}:{op.line}:")
                print(
                    f"Compiler Error : print is not defined for following type")
                exit(1)

            c_code += compile_expression(value_stack, type_stack)
            c_code += ");\n"

        elif op.type == OpType.OpGoto:
            label = op.oprands[-2]
            c_code += f"goto {label};\n"

        elif op.type == OpType.OpLabel:
            label = op.oprands[-1]
            c_code += f"{label}:\n"

    return c_code


def compile_program(program: Program) -> str:

    c_code = """
# include<stdio.h>

typedef int i32;
typedef long long i64;

typedef float f32;
typedef double f64;

typedef unsigned char bool;
typedef unsigned char byte;

typedef i64 ptr;

void print_i32(i32 a) {printf(\"%d\", a);}
void print_i64(i64 a) {printf(\"%lld\", a);}

void print_f32(f32 a) {printf(\"%f\", a);}
void print_f64(f64 a) {printf(\"%lf\", a);}

void print_bool(bool a) {printf(\"%s\", a?"true":"false");}
void print_byte(byte a) {printf(\"%c\", a);}

void print_ptr(ptr a) {printf(\"^%lld\", a);}

int main() {
"""
    c_code += f"byte global_memory[{program.global_memory}];\n"
    c_code += compile_program_partial(program)
    c_code += """return 0;
}
"""

    return c_code
