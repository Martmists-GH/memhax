import sys
from typing import Optional, Type, Self, Union

from memhax.element import PackedElement


class uintX_t(PackedElement[int]):
    @classmethod
    def fmt(cls) -> str:
        return f"{cls.num_bytes()}B"

    def get(self) -> int:
        _bytes = super().get()
        _size = self.num_bytes()
        if sys.byteorder == "big":
            _bytes = _bytes[::-1]
        return sum(_bytes[i] << (8 * i) for i in range(_size))

    def set(self, value: Union[Self, int]) -> int:
        if not isinstance(value, int):
            value = value()
        _bytes = [
            (value >> n) & 0xFF
            for n in range(self.num_bytes())
        ]
        if sys.byteorder == "big":
            _bytes = _bytes[::-1]
        super().set(tuple(_bytes))
        return value

    @classmethod
    def typename(cls, complete_type: Optional[Type[Self]] = None) -> str:
        return f"uint{cls.num_bytes() * 8}_t"

    @classmethod
    def num_bytes(cls) -> int:
        raise NotImplementedError


class uint8_t(uintX_t):
    @classmethod
    def num_bytes(cls) -> int:
        return 1


class uint16_t(uintX_t):
    @classmethod
    def num_bytes(cls) -> int:
        return 2


class uint32_t(uintX_t):
    @classmethod
    def num_bytes(cls) -> int:
        return 4


class uint64_t(uintX_t):
    @classmethod
    def num_bytes(cls) -> int:
        return 8
