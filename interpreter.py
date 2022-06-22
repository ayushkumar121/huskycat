from dataclasses import dataclass
from typing import List
from misc import operator_predence, operator_list, binary_operators, report_error, unary_operators
from parser import OpType, Program
from static_types import Primitives, TypedPtr, Types, type_str, size_of_primitive
from typechecker import apply_op_binary_on_types, apply_op_uinary_on_types


@dataclass
class Var:
    name: str
    type: Types
    size: int
    value: bytes


def apply_op_binary(a: int, b: int, op: str, tps: List[Types], global_memory: bytearray) -> int:
    if op == "+":
        return b + a
    elif op == "-":
        return b - a
    elif op == "/":
        return b / a
    elif op == "*":
        return b * a
    elif op == "%":
        return b % a
    elif op == "||":
        return 1 if (b or a) else 0
    elif op == "&&":
        return 1 if (b and a) else 0
    elif op == "<":
        return 1 if (b < a) else 0
    elif op == ">":
        return 1 if (b > a) else 0
    elif op == "==":
        return 1 if (b == a) else 0
    return 0


def apply_op_uinary(a: int, op: str, tp: Types, global_memory: bytearray) -> int:
    if op == "!":
        return 1 if (not a) else 0
    elif op == "^":
        if type(tp) == TypedPtr:
            return int.from_bytes(global_memory[a:a+size_of_primitive(tp.primitive)], "big")
        else:
            return global_memory[a]
    return 0


def evaluate_operation(value_stack: List[int], ops_stack: List[str], tp_stack: List[Types], global_memory: bytearray, file: str, line: int):
    op = ops_stack.pop()

    # Binary operators
    if op in binary_operators:
        a = value_stack.pop()
        a_tp = tp_stack.pop()

        b = value_stack.pop()
        b_tp = tp_stack.pop()

        value_stack.append(apply_op_binary(
            a, b, op, [a_tp, b_tp], global_memory))
        tp_stack.append(apply_op_binary_on_types(a_tp, b_tp, op))

    # Uninary operators
    elif op in unary_operators:
        a = value_stack.pop()
        a_tp = tp_stack.pop()

        value_stack.append(apply_op_uinary(a, op, a_tp, global_memory))
        tp_stack.append(apply_op_uinary_on_types(a_tp, op))


def evaluate_stack(eval_stack: List[int | str], type_stack: List[Types], global_memory: bytearray, file: str, line: int) -> tuple[List[int], List[Types]]:
    l = len(type_stack)

    tp_stack = []
    value_stack = []
    ops_stack = []

    for i, token in enumerate(eval_stack[::-1]):

        if str(token) == "(":
            ops_stack.append(token)

        elif str(token) == ")":
            while len(ops_stack) > 0 and ops_stack[-1] != "(":
                evaluate_operation(value_stack, ops_stack,
                                   global_memory, file, line)

            if len(ops_stack) > 0:
                ops_stack.pop()

        elif str(token) in operator_list:
            while len(ops_stack) > 0 and operator_predence(ops_stack[-1]) >= operator_predence(token):
                evaluate_operation(value_stack, ops_stack, tp_stack,
                                   global_memory, file, line)

            ops_stack.append(token)

        elif type(token) == type(0):
            value_stack.append(token)
            tp_stack.append(type_stack[l - (i+1)])

        else:
            report_error(
                f"unrecognised token `{token}` in eval stack", file, line)

    while len(ops_stack) > 0:
        evaluate_operation(value_stack, ops_stack, tp_stack,
                           global_memory, file, line)

    if len(value_stack) != 1 or len(tp_stack) != 1:
        report_error(
            f"unable to evalution following stack {eval_stack}", file, line)

    return value_stack, tp_stack


def find_var_scope(var: str, scopes: List[List[Var]]) -> tuple[int, int]:
    for i, scope in enumerate(scopes[::-1]):
        for j, v in enumerate(scope[::-1]):
            if v.name == var:
                return len(scopes) - (i + 1), len(scope) - (j+1)

    return -1, -1


def interpret_program(program: Program):

    type_stack: List[Types] = []
    value_stack: List[int | str] = []
    scopes: List[List[Var]] = []

    global_memory = bytearray(program.global_memory_capacity)

    assert len(OpType) == 9, "Exhaustive handling of operations"

    skip_elseif_else = False
    ip = 0

    while ip < len(program.operations):
        op = program.operations[ip]

        if op.type == OpType.OpBeginScope:

            vars = []
            for opi, opr in enumerate(op.oprands[1:][::-1]):
                var = opr
                tp = op.types[len(op.oprands) - (opi+1)]

                if type(tp) == Primitives:
                    vars.append(Var(var, tp, size_of_primitive(
                        tp), bytearray(size_of_primitive(tp))))
                elif type(tp) == TypedPtr:
                    vars.append(Var(var, tp, size_of_primitive(Primitives.I64),
                                    bytearray(size_of_primitive(Primitives.I64))))
                else:
                    report_error(
                        f"definition of type {type_str(tp)} not defined", op.file, op.line)

            scopes.append(vars)
            ip += 1

        elif op.type == OpType.OpEndScope:
            scopes.pop()

            if len(op.oprands) > 0:
                ip = op.oprands[-1]
            else:
                ip += 1

        elif op.type == OpType.OpPush:
            value_stack = []
            type_stack = []

            for opr in op.oprands[::-1]:
                i, j = find_var_scope(opr, scopes)
                tp = scopes[i][j].type

                if i != -1:
                    val = 0

                    if tp in [Primitives.I32, Primitives.I64, Primitives.Byte,
                              Primitives.Bool]:
                        val = int.from_bytes(
                            scopes[i][j].value, "big")
                    elif tp in [Primitives.F32, Primitives.F64]:
                        val = float.from_bytes(
                            scopes[i][j].value, "big")

                    elif type(tp) == TypedPtr:
                        val = int.from_bytes(
                            scopes[i][j].value, "big")
                    else:
                        report_error(
                            f"evaluation of type `{tp} not supported", op.file, op.line)

                    value_stack.append(val)
                else:
                    value_stack.append(opr)

                type_stack.append(tp)

            ip += 1

        elif op.type == OpType.OpMov:
            var = op.oprands[-1]
            deref = op.oprands[-2]
            tp = op.types[-1]

            value_stack, type_stack = evaluate_stack(
                value_stack, type_stack, global_memory, op.file, op.line)
            i, j = find_var_scope(var, scopes)

            type_stack.pop()

            if deref:
                deref_index = int.from_bytes(
                    scopes[i][j].value, "big")

                if type(tp) == TypedPtr:
                    if deref_index + size_of_primitive(tp.primitive)-1 > program.global_memory_ptr - 1:
                        report_error(
                            f"trying to access unallocated memory", op.file, op.line)

                    bts = int(value_stack.pop()).to_bytes(
                        size_of_primitive(tp.primitive), "big")
                    for i, bt in enumerate(bts):
                        global_memory[deref_index + i] = bt
                else:
                    if deref_index > program.global_memory_ptr - 1:
                        report_error(
                            f"trying to access unallocated memory", op.file, op.line)

                    global_memory[deref_index] = int(value_stack.pop())

            elif tp in [Primitives.I32, Primitives.I64, Primitives.Byte, Primitives.Bool]:
                scopes[i][j].value = int(value_stack.pop()).to_bytes(
                    size_of_primitive(tp), "big")

            elif tp in [Primitives.F32, Primitives.F64]:
                scopes[i][j].value = float(value_stack.pop()).to_bytes(
                    size_of_primitive(tp), "big")

            elif type(tp) == TypedPtr:
                scopes[i][j].value = int(value_stack.pop()).to_bytes(
                    size_of_primitive(Primitives.I64), "big")
            else:
                report_error(
                    f"assignment for this type {type_str(tp)} not defined", op.file, op.line)

            ip += 1

        elif op.type == OpType.OpIf:
            tj = op.oprands[-1]

            value_stack, type_stack = evaluate_stack(
                value_stack, type_stack, global_memory, op.file, op.line)

            type_stack.pop()

            if value_stack.pop() < 1:
                skip_elseif_else = False
                ip += tj + 1
            else:
                skip_elseif_else = True
                ip += 1

        elif op.type == OpType.OpElseIf:
            if skip_elseif_else:
                tj = op.oprands[-1]
                ip += tj + 1
                continue

            tj = op.oprands[-1]

            value_stack, type_stack = evaluate_stack(
                value_stack, type_stack, global_memory, op.file, op.line)

            type_stack.pop()

            if value_stack.pop() < 1:
                skip_elseif_else = False
                ip += tj + 1
            else:
                skip_elseif_else = True
                ip += 1

        elif op.type == OpType.OpElse:
            if skip_elseif_else:
                tj = op.oprands[-1]
                ip += tj + 1
                continue

            ip += 1

        elif op.type == OpType.OpWhile:
            tj = op.oprands[-1]

            value_stack, type_stack = evaluate_stack(
                value_stack, type_stack, global_memory, op.file, op.line)

            type_stack.pop()

            if value_stack.pop() < 1:
                ip += tj + 1
            else:
                ip += 1

        elif op.type == OpType.OpPrint:
            tp = op.types[-1]

            value_stack, type_stack = evaluate_stack(
                value_stack, type_stack, global_memory, op.file, op.line)

            type_stack.pop()

            if tp in [Primitives.I32, Primitives.I64, Primitives.F32, Primitives.F64]:
                print(value_stack.pop(), end="")
            elif tp == Primitives.Byte:
                print(chr(value_stack.pop()), end="")
            elif tp == Primitives.Bool:
                print("true" if value_stack.pop() == 1 else "false", end="")
            elif type(tp) == TypedPtr:
                print(f"^{type_str(tp.primitive)}({value_stack.pop()})", end="")
            else:
                report_error(
                    f"undefined print for this type", op.file, op.line)

            ip += 1
