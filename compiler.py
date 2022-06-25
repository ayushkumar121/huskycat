from calendar import c
from typing import List
from misc import report_error
from parser import Function, OpType, Program
from static_types import FuncCall, FuncType, Primitives, TypedPtr, Types, type_str


def compile_expression(value_stack: List, type_stack: List[Types]) -> str:
    c_code = ""
    deref = False

    while len(value_stack) > 0:

        val = value_stack.pop()
        tp = type_stack.pop()

        if val == "^":
            deref = True
        else:
            if type(tp) == TypedPtr:
                if deref:
                    c_code += f"*(({type_str(tp.primitive)}*)(global_memory + {val}))"
                    deref = False
                else:
                    c_code += f"{val}"
            elif type(tp) == FuncCall:
                oprands = []
                out = type_str(tp.kind.outs[:].pop())
                ins = ",".join([type_str(opr) for opr in tp.kind.ins])

                c_code += f"(({out} (*)({ins}) )(funcs[{tp.name}]))("
                for i, opr in enumerate(tp.oprands):
                    oprands.append(compile_expression(opr, tp.types[i]))
                c_code += ",".join(oprands)
                c_code += f")"
            else:
                c_code += f"{val}"

    return c_code


def compile_operations(program: Program | Function) -> str:
    c_code = ""

    type_stack: List[Types] = []
    value_stack: List[int | str] = []

    assert len(OpType) == 10, "Exhaustive handling of operations"

    for op in program.operations:

        if op.type == OpType.OpBeginScope:
            c_code += "{\n"

            is_func = type(program) == Function
            n = len(program.signature.ins) if is_func else 0

            while len(op.oprands[1+n:]) > 0:
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
                elif type(tp) == TypedPtr:
                    c_code += f"ptr {var};\n"
                elif type(tp) == FuncType:
                    c_code += f"ptr {var};\n"
                else:
                    report_error(
                        f"type `{type_str(tp)}` not defined for compilation", op.file, op.line)

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
            if deref and type(tp) == TypedPtr:
                c_code += f"{type_str(tp.primitive)} *tmp_cast=({type_str(tp.primitive)}*)(global_memory+{var});\n"
                c_code += f"*tmp_cast="
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
            elif type(tp) == TypedPtr:
                c_code += f"print_ptr(\"{type_str(tp.primitive)}\", "
            else:
                report_error(
                    "print is not defined for following type", op.file, op.line)

            c_code += compile_expression(value_stack, type_stack)
            c_code += ");\n"

        elif op.type == OpType.OpReturn:
            c_code += "return "
            c_code += compile_expression(value_stack, type_stack)
            c_code += ";\n"
            pass

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

"""
    c_code += f"byte global_memory[{program.memory_capacity}];\n"

    for i, func in enumerate(program.funcs):
        out = func.signature.outs[:].pop()
        ins = ",".join(
            [f"{type_str(opr)} {func.operations[0].oprands[i+1]}" for i, opr in enumerate(func.signature.ins)])

        c_code += f"{type_str(out)} func_{i}({ins})"
        c_code += "\n{\n"
        c_code += compile_operations(func)
        c_code += "}\n"

    c_code += "ptr funcs[]={\n"
    for i, func in enumerate(program.funcs):
        c_code += f"(ptr)func_{i}\n"
    c_code += "};\n"

    c_code += "int main() {\n"
    c_code += compile_operations(program)
    c_code += """return 0;
}
"""

    return c_code
