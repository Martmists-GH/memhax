from textwrap import indent
from typing import TypeVar, get_args, Generic, List, Optional, Self, Type

from memhax.native.structs import _ForwardRoot
from memhax.utils import memory, CONFIG
from memhax.element import PackedElement, Element
from memhax.utils import instance_type_args

E = TypeVar('E', bound=Element)
T = TypeVar('T')
S = TypeVar('S')


class RawPointer(PackedElement[int]):
    @classmethod
    def fmt(cls) -> str:
        return "P"


class Pointer(PackedElement[E], _ForwardRoot):
    raw: RawPointer

    def __init__(self, address: int):
        super().__init__(address)
        self.raw = RawPointer(self.address)

    @classmethod
    def fmt(cls) -> str:
        return "P"

    @classmethod
    def typename(cls, complete_type: Optional[Type[Self]] = None) -> str:
        if complete_type is None or isinstance(complete_type, type):
            return "void*"
        _args = get_args(complete_type)
        _type = _args[0]
        return f"{_type.typename(_type)}*"

    def get(self) -> E:
        _args = instance_type_args(self)
        if _args is None:
            raise TypeError("Cannot get value of a void pointer")
        _type = _args[0]
        item = _type(self.raw())
        if isinstance(item, _ForwardRoot):
            item.set_root(self.root)
        return item

    def set(self, value: E) -> None:
        super().set(value.address)

    def repr_handler(self, visited: List[int]):
        _args = instance_type_args(self)

        if self.raw() == 0:
            return "NULL"
        if _args is None:
            return f"Pointer(0x{self.raw():X})"
        return super().repr_handler(visited)

    def repr_simple(self, visited: List[int]) -> str:
        child = self.get()
        if child.address in visited:
            child_repr = "..."
        else:
            child_repr = child.repr_handler(visited[:])
        if CONFIG["hide_pointers_repr"]:
            return child_repr
        else:
            return f"*{child_repr}"

    def repr_rich(self, visited: List[int]) -> str:
        child = self.get()
        if child.address in visited:
            child_repr = "..."
        else:
            child_repr = child.repr_handler(visited[:])
        return f"Pointer({child_repr})"


class _ArrayCommon(Element[List[E]], _ForwardRoot):
    @classmethod
    def alignment(cls) -> int:
        return 1

    @classmethod
    def sizeof(cls, instance: Optional[Self] = None) -> int:
        return 0

    @classmethod
    def typename(cls, complete_type: Optional[Type[Self]] = None) -> str:
        _args = get_args(complete_type)
        _type = _args[0]
        _size = _args[1] if len(_args) > 1 else ""
        if callable(_size):
            _size = ""

        return f"{_type.typename(_type)}[{_size}]"

    def set(self, value: T) -> None:
        original = self.get()
        if len(value) != len(original):
            raise ValueError("Cannot set array of different size")

        for old, new in zip(original, value):
            old(new)

    def __getitem__(self, item):
        return self.get()[item]

    def __setitem__(self, key, value):
        self.get()[key](value)

    def repr_simple(self, visited: List[int]) -> str:
        items = self.get()
        if CONFIG["pretty_repr"]:
            body = "\n" + ",\n".join(indent(item.repr_handler(visited[:]), "    ") for item in items) + "\n"
        else:
            body = ", ".join(item.repr_handler(visited[:]) for item in items)
        return f"[{body}]"

    def repr_rich(self, visited: List[int]) -> str:
        return f"{self.__class__.__name__}({self.repr_simple(visited)})"

    def set_root(self, root: 'Struct'):
        super().set_root(root)
        for child in self.get():
            if isinstance(child, _ForwardRoot):
                child.set_root(root)


class StaticSizeArray(_ArrayCommon[T], Generic[T, S]):
    def get(self) -> T:
        _type, _size = instance_type_args(self)
        items = []
        address = self.address

        _align = _type.alignment()
        _itemsize = _type.sizeof()

        for _ in range(_size):
            rem = (address % _align)
            if rem != 0:
                address += _align - rem

            items.append(_type(address))
            address += _itemsize
        return items


class PropertySizeArray(_ArrayCommon[T], Generic[T, S]):
    def get(self) -> T:
        _type, _size = instance_type_args(self)
        items = []
        address = self.address

        _align = _type.alignment()
        _itemsize = _type.sizeof()

        for _ in range(_size(self.root)):
            rem = (address % _align)
            if rem != 0:
                address += _align - rem

            items.append(_type(address))
            address += _itemsize
        return items


class NullTerminatedArray(_ArrayCommon[T], Generic[T]):
    def get(self) -> T:
        _type = instance_type_args(self)[0]
        items = []
        address = self.address

        _align = _type.alignment()
        _itemsize = _type.sizeof()

        while True:
            rem = (address % _align)
            if rem != 0:
                address += _align - rem

            with memory(address) as mem:
                if all(b == 0 for b in mem.read(_itemsize)):
                    return items

            items.append(_type(address))
            address += _itemsize


class NullTerminatedString(Element):
    def get(self) -> T:
        chars = []
        address = self.address
        while True:
            with memory(address) as mem:
                if (byte := mem.read(1)) == b"\x00":
                    return "".join(chars)

            chars.append(byte.decode())
            address += 1

    @classmethod
    def typename(cls, complete_type: Optional[Type[Self]] = None) -> str:
        return "char[]"

    @classmethod
    def alignment(cls) -> int:
        return 1

    @classmethod
    def sizeof(cls, instance: Optional[Self] = None) -> int:
        if instance is None:
            return 0
        return len(instance.get()) + 1

    def repr_simple(self, visited: List[int]) -> str:
        if self.address < 1000:
            return "INVALID_STRING"
        return repr(self.get())

    def repr_rich(self, visited: List[int]) -> str:
        return f"NullTerminatedString({self.repr_simple(visited)})"
