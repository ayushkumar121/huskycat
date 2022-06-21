from typing import List
from parser import OpType, Program
from static_types import Primitives, TypedPtr, Types, type_str


def compile_expression(value_stack: List, type_stack: List) -> str:
    c_code = ""
    deref = False

    while len(value_stack) > 0:

        val = value_stack.pop()
        tp = type_stack.pop()

        if val == "^":
            deref = True
        else:
            if deref:
                if type(tp) == TypedPtr:
                    c_code += f"*(({type_str(tp.primitive)}*)(global_memory + {val}))"
                else:
                    c_code += f"*(global_memory + {val})"
                
                deref = False
            else:
                c_code += f"{val}"

    return c_code


def compile_operations(program: Program) -> str:
    c_code = ""

    type_stack: List[Types] = []
    value_stack: List[int | str] = []

    assert len(OpType) == 9, "Exhaustive handling of operations"

    for op in program.operations:

        if op.type == OpType.OpBeginScope:
            c_code += "{\n"

            while len(op.oprands[1:]) > 0:
                var = op.oprands.pop()
                tp = op.types.pop()

                if tp == Primitives.I32:
                    c_code += f"i32 {var};\n"
                elif tp == Primitives.I64:
                    c_code += f"i64 {var};\n"
                elif tp == Primitives.F32:
                    c_code += f"f32 {var};\n"
                elif tp == Primitives.F64:
                    c_code += f"f64 {var};\n"
                elif tp == Primitives.Bool:
                    c_code += f"bool {var};\n"
                elif tp == Primitives.Byte:
                    c_code += f"byte {var};\n"
                elif tp == Primitives.Ptr:
                    c_code += f"ptr {var};\n"
                elif tp == Primitives.Ptr:
                    c_code += f"ptr {var};\n"
                elif type(tp) == TypedPtr:
                    c_code += f"ptr {var};\n"
                else:
                    print(f"{op.file}:{op.line}:")
                    print(
                        f"Compiler Error : type {type_str(tp)} not defined for compilation")
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

            c_code += "{\n"
            if deref:
                if type(tp) == TypedPtr:
                    c_code += f"{type_str(tp.primitive)} *tmp_cast=({type_str(tp.primitive)}*)(global_memory+{var});\n"
                    c_code += f"*tmp_cast="
                else:
                    c_code += f"global_memory[{var}]="
            else:
                c_code += f"{var}="

            c_code += compile_expression(value_stack, type_stack)
            c_code += f";\n"
            c_code += "}\n"

        elif op.type == OpType.OpIf:
            c_code += "if("
            c_code += compile_expression(value_stack, type_stack)
            c_code += ")"

        elif op.type == OpType.OpElseIf:
            c_code += "else if("
            c_code += compile_expression(value_stack, type_stack)
            c_code += ")"

        elif op.type == OpType.OpElse:
            c_code += "else"

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
                c_code += f"print_ptr(\"\", "
            elif type(tp) == TypedPtr:
                c_code += f"print_ptr(\"{type_str(tp.primitive)}\", "
            else:
                print(f"{op.file}:{op.line}:")
                print(
                    f"Compiler Error : print is not defined for following type")
                exit(1)

            c_code += compile_expression(value_stack, type_stack)
            c_code += ");\n"

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

void print_ptr(const char * type, ptr a) {printf(\"^%s(%lld)\",type, a);}

int main() {
"""
    c_code += f"byte global_memory[{program.global_memory_capacity}];\n"
    c_code += compile_operations(program)
    c_code += """return 0;
}
"""

    return c_code
