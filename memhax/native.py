from textwrap import indent
from typing import TypeVar, Callable, List, Union, Optional, Generic

from memhax.constants import CONFIG, memory
from memhax.proxy import Proxy, StructProxy


T = TypeVar('T')


class NullTerminatedString(Proxy[str]):
    def __init__(self, addr: int):
        super().__init__(addr, self._get, self._set)

    def rich_str(self, objs: List[int] = None) -> str:
        return repr(self._get())

    def _get(self) -> str:
        with memory(self.address) as mem:
            string = b""
            while (c := mem.read(1)) != b'\x00':
                string += c
            return string.decode("utf-8")

    def _set(self, value: str) -> None:
        with memory(self.address) as mem:
            mem.write(value.encode("utf-8") + b'\x00')

    def type_str(self):
        return f"char"


class Long(StructProxy[int]):
    def __init__(self, addr: int):
        super().__init__(addr, "q")

    def type_str(self):
        return "long"


class UnsignedLong(StructProxy[int]):
    def __init__(self, addr: int):
        super().__init__(addr, "Q")

    def type_str(self):
        return "unsigned long"


class Integer(StructProxy[int]):
    def __init__(self, addr: int):
        super().__init__(addr, "i")

    def type_str(self):
        return "int"


class UnsignedInteger(StructProxy[int]):
    def __init__(self, addr: int):
        super().__init__(addr, "I")

    def type_str(self):
        return "unsigned int"


class Short(StructProxy[int]):
    def __init__(self, addr: int):
        super().__init__(addr, "h")

    def type_str(self):
        return "short"


class UnsignedShort(StructProxy[int]):
    def __init__(self, addr: int):
        super().__init__(addr, "H")

    def type_str(self):
        return "unsigned short"


class Byte(StructProxy[int]):
    def __init__(self, addr: int):
        super().__init__(addr, "b")

    def type_str(self):
        return "byte"


class UnsignedByte(StructProxy[int]):
    def __init__(self, addr: int):
        super().__init__(addr, "B")

    def type_str(self):
        return "unsigned byte"


class Char(StructProxy[str]):
    def __init__(self, addr: int):
        super().__init__(addr, "c")

    def type_str(self):
        return "char"


class Float(StructProxy[float]):
    def __init__(self, addr: int):
        super().__init__(addr, "f")

    def type_str(self):
        return "float"


class Double(StructProxy[float]):
    def __init__(self, addr: int):
        super().__init__(addr, "d")

    def type_str(self):
        return "double"


class Boolean(StructProxy[bool]):
    def __init__(self, addr: int):
        super().__init__(addr, "?")

    def type_str(self):
        return "boolean"


class Py_size_t(StructProxy[int]):
    def __init__(self, addr: int):
        super().__init__(addr, "N")

    def type_str(self):
        return "Py_size_t"


class Py_ssize_t(StructProxy[int]):
    def __init__(self, addr: int):
        super().__init__(addr, "n")

    def type_str(self):
        return "Py_ssize_t"


class Pointer(StructProxy[Proxy[T]]):
    def __init__(self, addr: int, _type: Optional[Callable[[int], Proxy[T]]] = None):
        super().__init__(addr, "P")
        self._type = _type

    def type_str(self):
        return f"{self._get().type_str()}*"

    def rich_str(self, objs: List[int] = None) -> str:
        if objs is None:
            objs = []
        addr = self.raw()
        if addr == 0:
            return "NULL"
        if addr in objs:
            return "..."
        objs.append(addr)
        if self._type is None:
            return f"{self.__class__.__name__}(0x{addr:x})"
        child = self._get().rich_str(objs[:])
        if CONFIG["hide_pointers"]:
            return child
        return f"*{child}"

    def raw(self) -> int:
        return super()._get()

    def _get(self) -> Proxy[T]:
        if self._type is None:
            return Proxy(self.raw())
        return self._type(super()._get())

    def _set(self, value: Union[int, Proxy[T]]) -> None:
        if isinstance(value, Proxy):
            super()._set(value.address)
        else:
            super()._set(value)

    def __getattr__(self, item):
        return getattr(self._get(), item)


class _ArrayCommon(Generic[T]):
    def _get(self) -> List[Proxy[T]]:
        raise NotImplementedError()

    def alignment(self) -> int:
        return self._get()[0].alignment()

    def type_str(self):
        items = self._get()
        return f"{items[0].type_str()}[{len(items)}]"

    def rich_str(self, objs: List[int] = None) -> str:
        items = self._get()

        if objs is None:
            objs = []
        if CONFIG["pretty_print"]:
            body = "" if not items else "\n" + ",\n".join(indent(item.rich_str(objs[:]), "    ") for item in items) + "\n"
        else:
            body = ', '.join([item.rich_str(objs[:]) for item in items])
        return f"[{body}]"

    def __getitem__(self, item):
        return self._get()[item]

    def __setitem__(self, key, value):
        self._get()[key](value)


class StaticSizeArray(_ArrayCommon[T], StructProxy[List[Proxy[T]]]):
    def __init__(self, addr: int, _type: Callable[[int], Proxy[T]], size: int):
        super().__init__(addr, f"{size}P")
        self._type = _type
        self._items = []

        offset = 0

        def _align():
            nonlocal offset
            dummy = _type(0)
            alignment = dummy.alignment()
            rem = (self.address + offset) % alignment
            if rem != 0:
                offset += rem

        for i in range(size):
            _align()
            item = _type(self.address + offset)
            self._items.append(item)
            offset += item.sizeof()

    def _get(self) -> List[Proxy[T]]:
        return self._items

    def _set(self, value: List[Proxy[T]]) -> None:
        if len(value) != len(self._items):
            raise ValueError("Array size mismatch")

        for old, new in zip(self._items, value):
            old(new)


class DynamicSizeArray(_ArrayCommon[T], Proxy[List[Proxy[T]]]):
    def __init__(self, addr: int, _type: Callable[[int], Proxy[T]], size: Callable[[], int]):
        super().__init__(addr, self._get, self._set)
        self._type = _type
        self._length = size

    def _get(self) -> List[Proxy[T]]:
        items = []
        offset = 0

        def _align():
            nonlocal offset
            dummy = self._type(0)
            alignment = dummy.alignment()
            rem = (self.address + offset) % alignment
            if rem != 0:
                offset += rem

        for i in range(self._length()):
            _align()
            item = self._type(self.address + offset)
            items.append(item)
            offset += item.sizeof()

        return items

    def _set(self, value: List[Proxy[T]]) -> None:
        if len(value) != self._length():
            raise ValueError("Array size mismatch")

        original = self._get()
        for old, new in zip(original, value):
            old(new)


class NullTerminatedArray(_ArrayCommon[T], Proxy[List[Proxy[T]]]):
    def __init__(self, addr: int, _type: Callable[[int], Proxy[T]]):
        super().__init__(addr, self._get, self._set)
        self._type = _type

    def _get(self) -> List[Proxy[T]]:
        items = []
        offset = 0

        def _align():
            nonlocal offset
            dummy = self._type(0)
            alignment = dummy.alignment()
            rem = (self.address + offset) % alignment
            if rem != 0:
                offset += rem

        for i in range(self._length()):
            _align()
            item = self._type(self.address + offset)
            MEMORY.seek(self.address + offset)
            if all(x == b"\0" for x in MEMORY.read(item.sizeof())):
                break
            items.append(item)
            offset += item.sizeof()

        return items

    def _set(self, value: List[Proxy[T]]) -> None:
        original = self._get()
        if len(value) != len(original):
            raise ValueError("Array size mismatch")

        for old, new in zip(original, value):
            old(new)
