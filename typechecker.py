from pickle import FALSE
from typing import List
from misc import not_implemented
from parser import OpType, Primitives, Program


def typecheck_program(program: Program):
    type_stack: List[Primitives] = []

    for op in program.operations:
        if op.type == OpType.OpBeginScope:
            pass

        elif op.type == OpType.OpEndScope:
            pass

        elif op.type == OpType.OpPush:
            while len(op.oprands) > 0:
                op.oprands.pop()
                type = op.types.pop()

                type_stack.append(type)

        elif op.type == OpType.OpMov:
            op.oprands.pop()
            type = op.types.pop()

            if len(type_stack) == 0:
                print(f"{op.file}:{op.line}:")
                print(f"Typecheck error: attempting to typecheck an empty typestack")
                exit(1)

            while len(type_stack) > 0:
                top = type_stack.pop()
                if top != Primitives.Unknown and top != type:
                    print(f"{op.file}:{op.line}:")
                    print(f"Typecheck error: mismatch type on assignment, expected {type} found {top}")
                    exit(1)

        elif op.type == OpType.OpPrint:
            pass

