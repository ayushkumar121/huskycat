from dataclasses import dataclass
from enum import Enum, auto

class Primitives(Enum):
    Byte = auto()
    I32 = auto()
    I64 = auto()
    F32 = auto()
    F64 = auto()
    Bool = auto()
    Ptr = auto()
    Operator = auto()
    Unknown = auto()

@dataclass
class TypedPtr():
    primitive: Primitives

Types = Primitives | TypedPtr

def size_of_primitive(primitive: Primitives) -> int:
    if primitive in [Primitives.I32, Primitives.F32]:
        return 4
    elif primitive in [Primitives.I64, Primitives.F64, Primitives.Ptr]:
        return 8
    elif primitive in [Primitives.Bool, Primitives.Byte]:
        return 1

    return 8

def type_str(tp: Types) -> str:
    if tp == Primitives.I32:
        return "i32"
    elif tp == Primitives.I64:
        return "i64"
    elif tp == Primitives.F32:
        return "f32"
    elif tp ==Primitives.F64:
        return  "f64"
    elif tp == Primitives.Bool:
        return "bool"
    elif tp == Primitives.Byte:
        return "byte"
    elif tp == Primitives.Ptr:
        return "ptr"
    elif type(tp) == TypedPtr:
        return f"^{type_str(tp.primitive)}"

    return "???"