from dataclasses import dataclass
from typing import List
from misc import operator_predence, operator_list, binary_operators, unary_operators
from parser import OpType, Program
from static_types import Primitives, TypedPtr, Types, type_str, size_of_primitive


@dataclass
class Var:
    name: str
    type: Types
    size: int
    value: bytes


def apply_op_binary(a: int, b: int, op: str, global_memory: bytearray) -> int:
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


def apply_op_uinary(a: int, op: str, global_memory: bytearray) -> int:
    if op == "!":
        return 1 if (not a) else 0
    elif op == "^":
        return global_memory[a]
    return 0


def evaluate_operation(value_stack: List[int], ops_stack: List[str], global_memory: bytearray, file: str, line: int):
    op = ops_stack.pop()

    # Binary operators
    if op in binary_operators:
        a = value_stack.pop()
        b = value_stack.pop()

        value_stack.append(apply_op_binary(a, b, op, global_memory))

    # Uninary operators
    elif op in unary_operators:
        a = value_stack.pop()
        value_stack.append(apply_op_uinary(a, op, global_memory))


def evaluate_stack(eval_stack: List[int | str], global_memory: bytearray, file: str, line: int) -> tuple[List[int]]:
    value_stack = []
    ops_stack = []

    for token in eval_stack[::-1]:
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
                evaluate_operation(value_stack, ops_stack,
                                   global_memory, file, line)

            ops_stack.append(token)

        elif type(token) == type(0):
            value_stack.append(token)
        else:
            print(f"{file}:{line}:")
            print(
                f"Interpreter Error : unrecognised token `{token}` in eval stack")
            exit(1)

    while len(ops_stack) > 0:
        evaluate_operation(value_stack, ops_stack, global_memory, file, line)

    if len(value_stack) != 1:
        print(f"{file}:{line}:")
        print(
            f"Interpreter Error : unable to evalution following stack {eval_stack}")
        exit(1)

    return value_stack


def find_var_scope(var: str, scopes: List[List[Var]]) -> tuple[int, int]:
    for i, scope in enumerate(scopes[::-1]):
        for j, v in enumerate(scope[::-1]):
            if v.name == var:
                return len(scopes) - (i + 1), len(scope) - (j+1)

    return -1, -1


def interpret_program(program: Program):
    value_stack: List[int | str] = []
    scopes: List[List[Var]] = []

    global_memory = bytearray(program.global_memory)

    assert len(OpType) == 9, "Exhaustive handling of operations"

    skip_elseif_else = False
    ip = 0

    while ip < len(program.operations):
        op = program.operations[ip]

        if op.type == OpType.OpBeginScope:

            vars = []
            for opi, opr in enumerate(op.oprands[::-1]):
                var = opr
                tp = op.types[len(op.oprands) - (opi+1)]

                if type(tp) == Primitives:
                    vars.append(Var(var, tp, size_of_primitive(
                        tp), bytearray(size_of_primitive(tp))))
                elif type(tp) == TypedPtr:
                    vars.append(Var(var, tp, size_of_primitive(Primitives.Ptr),
                                    bytearray(size_of_primitive(Primitives.Ptr))))
                else:
                    print(f"{op.file}:{op.line}:")
                    print(
                        f"Interpreter Error : definition of type {type_str(tp)} not defined")
                    exit(1)
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

            for opr in op.oprands[::-1]:
                i, j = find_var_scope(opr, scopes)

                if i != -1:
                    val = 0
                    tp = scopes[i][j].type

                    if tp in [Primitives.I32, Primitives.I64, Primitives.Byte,
                              Primitives.Bool, Primitives.Ptr]:
                        val = int.from_bytes(
                            scopes[i][j].value, "big")
                    elif tp in [Primitives.F32, Primitives.F64]:
                        val = float.from_bytes(
                            scopes[i][j].value, "big")

                    elif type(tp) == TypedPtr:
                        val = int.from_bytes(
                            scopes[i][j].value, "big")
                    else:
                        print(f"{op.file}:{op.line}:")
                        print(
                            f"Interpreter Error : evaluation of type `{tp} not supported`")
                        exit(1)

                    value_stack.append(val)
                else:
                    value_stack.append(opr)

            ip += 1

        elif op.type == OpType.OpMov:
            var = op.oprands[-1]
            deref = op.oprands[-2]
            tp = op.types[-1]

            value_stack = evaluate_stack(
                value_stack, global_memory, op.file, op.line)
            i, j = find_var_scope(var, scopes)

            if deref:
                deref_index = int.from_bytes(
                    scopes[i][j].value, "big")

                if deref_index > program.global_memory - 1:
                    print(f"{op.file}:{op.line}:")
                    print(
                        f"Interpreter Error : cannot access more memory than allocated")
                    exit(1)

                global_memory[deref_index] = int(value_stack.pop())

            elif tp in [Primitives.I32, Primitives.I64, Primitives.Byte, Primitives.Bool, Primitives.Ptr]:
                scopes[i][j].value = int(value_stack.pop()).to_bytes(
                    size_of_primitive(tp), "big")

            elif tp in [Primitives.F32, Primitives.F64]:
                scopes[i][j].value = float(value_stack.pop()).to_bytes(
                    size_of_primitive(tp), "big")

            elif type(tp) == TypedPtr:
                scopes[i][j].value = int(value_stack.pop()).to_bytes(
                    size_of_primitive(Primitives.Ptr), "big")
            else:
                print(f"{op.file}:{op.line}:")
                print(
                    f"Interpreter Error : assignment for this type {type_str(tp)} not defined")
                exit(1)

            ip += 1

        elif op.type == OpType.OpIf:
            tj = op.oprands[-1]

            value_stack = evaluate_stack(
                value_stack, global_memory, op.file, op.line)

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

            value_stack = evaluate_stack(
                value_stack, global_memory, op.file, op.line)

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

            value_stack = evaluate_stack(
                value_stack, global_memory, op.file, op.line)

            if value_stack.pop() < 1:
                ip += tj + 1
            else:
                ip += 1

        elif op.type == OpType.OpPrint:
            tp = op.types[-1]

            value_stack = evaluate_stack(
                value_stack, global_memory, op.file, op.line)

            if tp in [Primitives.I32, Primitives.I64, Primitives.F32, Primitives.F64]:
                print(value_stack.pop(), end="")
            elif tp == Primitives.Byte:
                print(chr(value_stack.pop()), end="")
            elif tp == Primitives.Bool:
                print("true" if value_stack.pop() == 1 else "false", end="")
            elif tp == Primitives.Ptr:
                print(f"^({value_stack.pop()})", end="")
            elif type(tp) == TypedPtr:
                print(f"^{type_str(tp.primitive)}({value_stack.pop()})", end="")
            else:
                print(f"{op.file}:{op.line}:")
                print(
                    f"Interpreter Error : undefined print for this type")
                exit(1)

            ip += 1
