from typing import Self, Optional, Type

from memhax.element import PackedElement


class LongLong(PackedElement[int]):
    @classmethod
    def fmt(cls) -> str:
        return "q"

    @classmethod
    def typename(cls, complete_type: Optional[Type[Self]] = None) -> str:
        return "long long"


class UnsignedLongLong(PackedElement[int]):
    @classmethod
    def fmt(cls) -> str:
        return "Q"

    @classmethod
    def typename(cls, complete_type: Optional[Type[Self]] = None) -> str:
        return "unsigned long long"


class Long(PackedElement[int]):
    @classmethod
    def fmt(cls) -> str:
        return "l"

    @classmethod
    def typename(cls, complete_type: Optional[Type[Self]] = None) -> str:
        return "long"


class UnsignedLong(PackedElement[int]):
    @classmethod
    def fmt(cls) -> str:
        return "L"

    @classmethod
    def typename(cls, complete_type: Optional[Type[Self]] = None) -> str:
        return "unsigned long"


class Integer(PackedElement[int]):
    @classmethod
    def fmt(cls) -> str:
        return "i"

    @classmethod
    def typename(cls, complete_type: Optional[Type[Self]] = None) -> str:
        return "int"


class UnsignedInteger(PackedElement[int]):
    @classmethod
    def fmt(cls) -> str:
        return "I"

    @classmethod
    def typename(cls, complete_type: Optional[Type[Self]] = None) -> str:
        return "unsigned int"


class Short(PackedElement[int]):
    @classmethod
    def fmt(cls) -> str:
        return "h"

    @classmethod
    def typename(cls, complete_type: Optional[Type[Self]] = None) -> str:
        return "short"


class UnsignedShort(PackedElement[int]):
    @classmethod
    def fmt(cls) -> str:
        return "H"

    @classmethod
    def typename(cls, complete_type: Optional[Type[Self]] = None) -> str:
        return "unsigned short"


class Byte(PackedElement[int]):
    @classmethod
    def fmt(cls) -> str:
        return "b"

    @classmethod
    def typename(cls, complete_type: Optional[Type[Self]] = None) -> str:
        return "byte"


class UnsignedByte(PackedElement[int]):
    @classmethod
    def fmt(cls) -> str:
        return "B"

    @classmethod
    def typename(cls, complete_type: Optional[Type[Self]] = None) -> str:
        return "unsigned byte"


class Float(PackedElement[float]):
    @classmethod
    def fmt(cls) -> str:
        return "f"

    @classmethod
    def typename(cls, complete_type: Optional[Type[Self]] = None) -> str:
        return "float"


class Double(PackedElement[float]):
    @classmethod
    def fmt(cls) -> str:
        return "d"

    @classmethod
    def typename(cls, complete_type: Optional[Type[Self]] = None) -> str:
        return "double"


class Char(PackedElement[bytes]):
    @classmethod
    def fmt(cls) -> str:
        return "c"

    @classmethod
    def typename(cls, complete_type: Optional[Type[Self]] = None) -> str:
        return "char"


class Boolean(PackedElement[bool]):
    @classmethod
    def fmt(cls) -> str:
        return "?"

    @classmethod
    def typename(cls, complete_type: Optional[Type[Self]] = None) -> str:
        return "bool"


class Py_ssize_t(PackedElement[int]):
    @classmethod
    def fmt(cls) -> str:
        return "n"

    @classmethod
    def typename(cls, complete_type: Optional[Type[Self]] = None) -> str:
        return "Py_ssize_t"


class Py_size_t(PackedElement[int]):
    @classmethod
    def fmt(cls) -> str:
        return "N"

    @classmethod
    def typename(cls, complete_type: Optional[Type[Self]] = None) -> str:
        return "Py_size_t"
