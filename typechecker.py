from pprint import pprint
import re
from typing import List
from misc import operator_predence, operator_list, binary_operators, report_error, unary_operators
from parser import Function, OpType, Operation, Program
from static_types import FuncCall, Primitives, TypedPtr, Types, type_str


def find_scope_with_symbol(symbol: str, operations: Operation, global_scope: Operation) -> tuple[Operation, int]:
    skip = False
    for op in operations[::-1]:
        if op.type == OpType.OpBeginScope:
            if not skip and symbol in op.oprands:
                return op, op.oprands.index(symbol)
            skip = False
        elif op.type == OpType.OpEndScope:
            skip = True

    # Global Scope
    if symbol in global_scope.oprands:
        return global_scope, global_scope.oprands.index(symbol)

    return None, -1


def apply_op_binary_on_types(a: Types, b: Types, op: str, file: str, line: int) -> Types:
    if op in ["+",  "-", "*", "/"]:
        return b
    elif op == "%":
        return Primitives.I64
    elif op in ["||", "&&", ">", "<", "==", "!="]:
        return Primitives.Bool

    return Primitives.Unknown


def apply_op_uinary_on_types(a: Types, op: str, file: str, line: int) -> Types:
    if op == "!":
        return Primitives.Bool
    elif op == "^":
        if type(a) != TypedPtr:
            report_error(
                f"cannot deref type `{type_str(a)}`", file, line)

        return a.primitive

    return Primitives.Unknown


def evaluate_operation(type_stack: List[Types], ops_stack: List[str], file: str, line: int):
    op = ops_stack.pop()

    # Binary operators
    if op in binary_operators:
        a = type_stack.pop()
        b = type_stack.pop()

        if a != b:
            value_types = [Primitives.F32, Primitives.F64,
                           Primitives.I32, Primitives.I64]
            if not (a in value_types and b in value_types) and not (type(b) == TypedPtr and a in [Primitives.I32, Primitives.I64]):
                report_error(
                    f"binary operation `{type_str(b)}{op}{type_str(a)}` not supported", file, line)

        type_stack.append(apply_op_binary_on_types(a, b, op, file, line))

    # Uninary operators
    elif op in unary_operators:
        a = type_stack.pop()
        type_stack.append(apply_op_uinary_on_types(a, op, file, line))


def evaluate_stack(eval_stack: List[int | str],
                   types: List[Types],
                   file: str, line: int) -> tuple[List[int], List[Types]]:

    type_stack: List[Primitives] = []
    ops_stack: List[str] = []

    for i, token in enumerate(eval_stack[::-1]):
        i = len(eval_stack) - (i+1)

        if str(token) == "(":
            ops_stack.append(token)

        elif str(token) == ")":
            while len(ops_stack) > 0 and ops_stack[-1] != "(":
                evaluate_operation(type_stack, ops_stack, file, line)

            if len(ops_stack) > 0:
                ops_stack.pop()

        elif str(token) in operator_list:
            while len(ops_stack) > 0 and operator_predence(ops_stack[-1]) >= operator_predence(token):
                evaluate_operation(type_stack, ops_stack, file, line)

            ops_stack.append(token)

        else:
            type_stack.append(types[i])

    while len(ops_stack) > 0:
        evaluate_operation(type_stack, ops_stack, file, line)

    if len(type_stack) != 1:
        report_error(
            f"unable to type evaluate following stack {eval_stack}", file, line)
    return [0], type_stack


def typecheck_program(program: Program):
    typecheck_operations(program, program.operations[0])

    for func in program.funcs:
        typecheck_operations(func, program.operations[0])


def typecheck_operations(program: Program | Function, global_scope: Operation):
    type_stack: List[Types] = []
    value_stack: List[int | str] = []

    assert len(OpType) == 10, "Exhaustive handling of operations"

    for ip, op in enumerate(program.operations[:]):

        if op.type == OpType.OpBeginScope:
            pass

        elif op.type == OpType.OpEndScope:
            pass

        elif op.type == OpType.OpPush:
            value_stack = []
            type_stack = []

            for i, opr in enumerate(op.oprands[::-1]):
                val = opr
                tp = op.types[len(op.oprands) - (i+1)]

                if tp == Primitives.Untyped:
                    foundop, j = find_scope_with_symbol(
                        val, program.operations[:ip], global_scope)

                    tp = foundop.types[j]
                    op.types[len(op.oprands) - (i+1)] = tp

                if type(tp) == FuncCall:
                    foundop, j = find_scope_with_symbol(
                        tp.name, program.operations[:ip], global_scope)

                    tp = foundop.types[j].outs[:].pop()
                    op.types[len(op.oprands) - (i+1)
                             ].signature = foundop.types[j]

                    expected = foundop.types[j].ins
                    found_stack = []

                    oprands = op.types[len(op.oprands) - (i+1)].oprands
                    types = op.types[len(op.oprands) - (i+1)].types

                    for k, opr in enumerate(oprands):
                        t = Primitives.Untyped
                        vals, tps = evaluate_stack(
                            opr, types[k], op.file, op.line)

                        v = vals.pop()
                        t = tps.pop()
                        if t == Primitives.Untyped:
                            foundop, oprr = find_scope_with_symbol(
                                opr[-1], program.operations[:ip], global_scope)

                            t = foundop.types[oprr]

                        found_stack.append(t)

                    if expected != found_stack:
                        expected_str = ",".join(
                            [type_str(t) for t in expected])
                        found_str = ",".join([type_str(t)
                                             for t in found_stack])
                        report_error(
                            f"unexpected function call expected ({expected_str}) but found ({found_str})", op.file, op.line)

                value_stack.append(val)
                type_stack.append(tp)

        elif op.type == OpType.OpMov:
            if len(type_stack) == 0:
                report_error(
                    f"attempting to typecheck an empty typestack", op.file, op.line)

            symbol = op.oprands[-1]
            deref = op.oprands[-2]
            tp = op.types[-1]

            if deref:
                if type(tp) == TypedPtr:
                    tp = tp.primitive
                else:
                    report_error(
                        f"cannot deref type `{type_str(tp)}`", op.file, op.line)

            value_stack, type_stack = evaluate_stack(
                value_stack, type_stack, op.file, op.line)

            value_stack.pop()
            found = type_stack.pop()

            if tp == Primitives.Untyped:
                foundop, j = find_scope_with_symbol(
                    symbol, program.operations[:ip], global_scope)
                op.types[-1] = found
                foundop.types[j] = found
            elif tp != found:
                report_error(
                    f"mismatch type on assignment, expected `{type_str(tp)}` found `{type_str(found)}`", op.file, op.line)

        elif op.type == OpType.OpIf:
            if len(type_stack) == 0:
                report_error(
                    f"attempting to typecheck an empty typestack`", op.file, op.line)

            value_stack, type_stack = evaluate_stack(
                value_stack, type_stack, op.file, op.line)

            value_stack.pop()
            found = type_stack.pop()
            if found != Primitives.Bool:
                report_error(
                    f"unexpected type on if expression, expected `bool` found `{type_str(found)}`", op.file, op.line)

        elif op.type == OpType.OpElseIf:
            if len(type_stack) == 0:
                report_error(
                    f"attempting to typecheck an empty typestack", op.file, op.line)

            value_stack, type_stack = evaluate_stack(
                value_stack, type_stack, op.file, op.line)

            value_stack.pop()
            found = type_stack.pop()
            if found != Primitives.Bool:
                report_error(
                    f"unexpected type on else if expression, expected `bool` found `{type_str(found)}`", op.file, op.line)

        elif op.type == OpType.OpElse:
            pass

        elif op.type == OpType.OpWhile:
            if len(type_stack) == 0:
                report_error(
                    f"attempting to typecheck an empty typestack", op.file, op.line)

            value_stack, type_stack = evaluate_stack(
                value_stack, type_stack, op.file, op.line)

            value_stack.pop()
            found = type_stack.pop()
            if found != Primitives.Bool:
                report_error(
                    f"unexpected type on while expression, expected `bool` found `{type_str(found)}", op.file, op.line)

        elif op.type == OpType.OpPrint:
            value_stack, type_stack = evaluate_stack(
                value_stack, type_stack, op.file, op.line)

            value_stack.pop()
            op.types.append(type_stack.pop())

        elif op.type == OpType.OpReturn:
            if len(type_stack) == 0:
                report_error(
                    f"attempting to typecheck an empty typestack", op.file, op.line)

            value_stack, type_stack = evaluate_stack(
                value_stack, type_stack, op.file, op.line)

            return_type = program.signature.outs[:].pop()

            value_stack.pop()
            found = type_stack.pop()
            if found != return_type:
                report_error(
                    f"unexpected return type for function expected `{type_str(return_type)}` found `{type_str(found)}`", op.file, op.line)
            pass
