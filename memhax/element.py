from __future__ import annotations

from struct import calcsize, unpack, pack
from typing import TypeVar, Self, Union, Optional, Generic, get_type_hints, Type, List

from memhax.utils import memory, CONFIG

T = TypeVar('T')


class Element(Generic[T]):
    def __init__(self, address: int):
        self.address = address

    def __call__(self, instance: Optional[Union[Self, T]] = None) -> T:
        if instance is None:
            return self.get()
        else:
            return self.set(instance)

    def get(self) -> T:
        raise NotImplementedError(self.__class__.__name__)

    def set(self, value: Union[Self, T]) -> T:
        raise NotImplementedError(self.__class__.__name__)

    @classmethod
    def alignment(cls) -> int:
        raise NotImplementedError(cls.__name__)

    @classmethod
    def sizeof(cls, instance: Optional[Self] = None) -> int:
        raise NotImplementedError(cls.__name__)

    @classmethod
    def typename(cls, complete_type: Optional[Type[Self]] = None) -> str:
        raise NotImplementedError(cls.__name__)

    def repr_handler(self, visited: List[int]):
        visited.append(self.address)
        if CONFIG["simplified_repr"]:
            return self.repr_simple(visited[:])
        else:
            return self.repr_rich(visited[:])

    def repr_simple(self, visited: List[int]) -> str:
        return self.repr_rich(visited[:])

    def repr_rich(self, visited: List[int]) -> str:
        return super().__repr__()

    def __repr__(self):
        return self.repr_handler([])


class PackedElement(Element[T]):
    @classmethod
    def fmt(cls) -> str:
        raise NotImplementedError(cls.__name__)

    @classmethod
    def alignment(cls) -> int:
        return calcsize("@"+cls.fmt())

    @classmethod
    def sizeof(cls, instance: Optional[Self] = None) -> int:
        return calcsize("@"+cls.fmt())

    def get(self) -> T:
        with memory(self.address) as mem:
            item = unpack("@"+self.fmt(), mem.read(self.sizeof()))
        return item[0] if len(item) == 1 else item

    def set(self, value: Union[Self, T]) -> T:
        with memory(self.address) as mem:
            if self.__class__ == value.__class__:
                value = value()
            if isinstance(value, tuple):
                mem.write(pack("@"+self.fmt(), *value))
            else:
                mem.write(pack("@"+self.fmt(), value))
        return value

    def repr_simple(self, visited: List[int]) -> str:
        return repr(self.get())

    def repr_rich(self, visited: List[int]) -> str:
        return f"{self.__class__.__name__}({self.get()})"
