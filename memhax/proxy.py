from __future__ import annotations

from textwrap import indent
from typing import Generic, TypeVar, Callable, Optional, Union, List, Dict, Any
from struct import pack, unpack, calcsize

from memhax.constants import CONFIG, memory

T = TypeVar('T')
R = TypeVar('R')


class Proxy(Generic[T]):
    def __init__(self, addr: int, getter: Optional[Callable[[], T]] = None, setter: Optional[Callable[[Union[T, Proxy[T]]], None]] = None, size: int = 0):
        def _throwNotImplemented(*args):
            raise NotImplementedError("No getter or setter defined for this proxy")

        self.address = addr
        self._getter = getter or _throwNotImplemented
        self._setter = setter or _throwNotImplemented
        self._offset = 0
        self._size = size
        self._fields: Dict[str, Proxy[Any]] = {}

    def _align(self, _type: Callable[[int], Proxy[Any]]) -> None:
        dummy = _type(0)
        alignment = dummy.alignment()
        rem = (self.address + self._offset) % alignment
        if rem != 0:
            self._offset += rem

    def _property(self, name: str, _type: Callable[[int], Proxy[R]]) -> Proxy[R]:
        self._align(_type)

        self._fields[name] = obj = _type(self.address + self._offset)
        self._offset += obj.sizeof()
        return obj

    def __getattr__(self, item) -> Proxy[Any]:
        return self._fields[item]

    def __call__(self, arg: Optional[Union[T, Proxy[T]]] = None) -> T:
        if arg is not None:
            self._setter(arg)
            return arg
        return self._getter()

    def alignment(self) -> int:
        raise NotImplementedError(self.__class__.__name__)

    def sizeof(self) -> int:
        return self._size + self._offset

    def offsetof(self, field: Proxy[Any]) -> int:
        return field.address - self.address

    def offsetafter(self, field: Proxy[Any]) -> int:
        return field.address + field.sizeof() - self.address

    # === Properties ===

    def long(self, name: str) -> Proxy[int]:
        from memhax.native import Long
        return self._property(name, Long)

    def ulong(self, name: str) -> Proxy[int]:
        from memhax.native import UnsignedLong
        return self._property(name, UnsignedLong)

    def int(self, name: str) -> Proxy[int]:
        from memhax.native import Integer
        return self._property(name, Integer)

    def uint(self, name: str) -> Proxy[int]:
        from memhax.native import UnsignedInteger
        return self._property(name, UnsignedInteger)

    def short(self, name: str) -> Proxy[int]:
        from memhax.native import Short
        return self._property(name, Short)

    def ushort(self, name: str) -> Proxy[int]:
        from memhax.native import UnsignedShort
        return self._property(name, UnsignedShort)

    def byte(self, name: str) -> Proxy[int]:
        from memhax.native import Byte
        return self._property(name, Byte)

    def ubyte(self, name: str) -> Proxy[int]:
        from memhax.native import UnsignedByte
        return self._property(name, UnsignedByte)

    def char(self, name: str) -> Proxy[str]:
        from memhax.native import Char
        return self._property(name, Char)

    def float(self, name: str) -> Proxy[float]:
        from memhax.native import Float
        return self._property(name, Float)

    def double(self, name: str) -> Proxy[float]:
        from memhax.native import Double
        return self._property(name, Double)

    def boolean(self, name: str) -> Proxy[bool]:
        from memhax.native import Boolean
        return self._property(name, Boolean)

    def size_t(self, name: str) -> Proxy[int]:
        from memhax.native import Py_size_t
        return self._property(name, Py_size_t)

    def ssize_t(self, name: str) -> Proxy[int]:
        from memhax.native import Py_ssize_t
        return self._property(name, Py_ssize_t)

    def struct(self, name: str, _type: Callable[[int], Struct[R]]) -> Struct[R]:
        self._align(_type)

        item = _type(self.address + self._offset)
        self._offset += item.sizeof()
        self._fields[name] = item
        return item

    def pointer(self, name: str, from_addr: Optional[Callable[[int], Proxy[R]]] = None) -> Proxy[R]:
        from memhax.native import Pointer
        obj = self._property(name, lambda addr: Pointer(addr, from_addr))
        self._fields[name] = obj
        return obj

    def array(self, name: str, _type: Callable[[int], Proxy[R]], length: Union[int, Callable[[], int]]) -> Proxy[R]:
        from memhax.native import StaticSizeArray, DynamicSizeArray
        _array_type = StaticSizeArray if isinstance(length, int) else DynamicSizeArray
        self._align(lambda addr: _array_type(addr, _type, length))

        obj = _array_type(self.address + self._offset, _type, length)
        self._offset += obj.sizeof()
        self._fields[name] = obj
        return obj

    def type_str(self) -> str:
        raise NotImplementedError(self.__class__.__name__)

    def rich_str(self, objs: List[int] = None) -> str:
        if objs is None:
            objs = []
        if CONFIG["pretty_print"]:
            body = "\n" + ",\n".join(indent(f"{k}={v.rich_str(objs)}", "    ") for k, v in sorted(self._fields.items(), key=lambda x: self.offsetof(x[1]))) + "\n"
        else:
            body = ', '.join(f'{k}={v.rich_str(objs[:])}' for k, v in sorted(self._fields.items(), key=lambda x: self.offsetof(x[1])))
        return f"{self.__class__.__name__}({body})"

    def __repr__(self) -> str:
        return self.rich_str()


class Struct(Proxy[None]):
    def __init__(self, addr: int):
        super().__init__(addr, lambda: None, lambda v: None, 0)

    def alignment(self) -> int:
        return min(self._fields.values(), key=lambda x: self.offsetof(x)).alignment()

    def _reinterpret(self, addr: int) -> Any:
        dummy = (1,)
        from memhax.cpython.collections import PyTupleObject
        _tup_repr = PyTupleObject(id(dummy))
        _ptr_arr = _tup_repr.ob_item()
        _ptr_arr[0](addr)
        return dummy[0]

    def type_str(self) -> str:
        return self.__class__.__name__

    def struct_str(self) -> str:
        pairs = [(field.type_str(), name) for (name, field) in sorted(self._fields.items(), key=lambda x: self.offsetof(x[1]))]
        longest = max(len(_type) for _type, name in pairs)
        fields = '\n'.join(f"    {field.type_str():<{longest}} {name};" for (name, field) in self._fields.items())
        return f"struct {self.__class__.__name__} {{\n{fields}\n}}"

    def __call__(self, arg: Optional[Union[T, Proxy[T]]] = None) -> T:
        if arg is not None:
            raise NotImplementedError
        return self._reinterpret(self.address)


class StructProxy(Proxy[T]):
    def __init__(self, addr: int, fmt: str):
        super().__init__(addr, self._get, self._set, calcsize(fmt))
        self._fmt = fmt

    def alignment(self) -> int:
        return calcsize(self._fmt)

    def rich_str(self, objs: List[int] = None) -> str:
        return repr(self._get())

    def _get(self) -> T:
        with memory(self.address) as mem:
            return unpack(self._fmt, mem.read(self.sizeof()))[0]

    def _set(self, value: Union[T, Proxy[T]]) -> None:
        with memory(self.address) as mem:
            try:
                data = pack(self._fmt, value)
            except TypeError:
                data = pack(self._fmt, value())
            mem.write(data)
