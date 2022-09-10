from textwrap import indent
from typing import get_type_hints, Optional, Self, Type, TypeVar, List

from memhax.element import Element
from memhax.utils import CONFIG

T = TypeVar('T')


class StructMember:
    def __init__(self, name: str, parent: type):
        self.name = name
        self.parent = parent
        self._hints = None

    @property
    def hints(self) -> dict:
        if self._hints is None:
            self._hints = get_type_hints(self.parent)
        return self._hints

    @property
    def type(self) -> Type[Element]:
        cls = self.hints[self.name]
        if hasattr(cls, "__orig_class__"):
            cls = cls.__orig_class__
        return cls

    @property
    def size(self) -> int:
        return self.type.sizeof()

    @property
    def alignment(self) -> int:
        return self.type.alignment()


class StructMeta(type):
    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        cls._struct_fields = []

        for parent_class in bases:
            if hasattr(parent_class, '_struct_fields'):
                cls._struct_fields.extend(parent_class._struct_fields)

        for (_name, _) in getattr(cls, '__annotations__', {}).items():
            member = StructMember(_name, cls)
            setattr(cls, _name, member)
            cls._struct_fields.append(member)
        return cls

    def __repr__(self):
        entries = [
            (member.type.typename(member.type), member.name)
            for member in self._struct_fields
        ]
        longest = max(len(typename) for (typename, name) in entries)
        body = "\n".join(
            f"    {typename:<{longest}} {name};"
            for typename, name in entries
        )
        return f"struct {self.__name__} {{\n{body}\n}}"


class Struct(Element[T], metaclass=StructMeta):
    def __init__(self, address: int):
        super().__init__(address)
        self._offset = 0

        # noinspection PyProtectedMember
        for member in self.__class__._struct_fields:
            self._align(member.alignment)
            item = member.type(address + self._offset)
            if isinstance(item, _ForwardRoot):
                item.set_root(self)
            self._offset += member.size

            setattr(self, member.name, item)

    def _align(self, to: int) -> None:
        rem = (self.address + self._offset) % to
        if rem != 0:
            self._offset += to - rem

    @classmethod
    def alignment(cls) -> int:
        return max(item.alignment() for item in get_type_hints(cls).values())

    @classmethod
    def sizeof(cls, instance: Optional[Self] = None) -> int:
        offset = 0
        for member in cls._struct_fields:
            _type = member.type
            align = _type.alignment()
            rem = offset % align
            if rem != 0:
                offset += align - rem
            offset += _type.sizeof(getattr(instance, member.name, instance))
        return offset

    @classmethod
    def offsetof(cls, field) -> int:
        offset = 0
        for member in cls._struct_fields:
            if member.name == field.name:
                return offset
            rem = offset % member.alignment
            if rem != 0:
                offset += member.alignment - rem
            offset += member.size
        raise ValueError(f'Field {field.name} not found in {cls.__name__}')

    @classmethod
    def offset_after(cls, field) -> int:
        return cls.offsetof(field) + field.size

    @classmethod
    def typename(cls, complete_type: Optional[Type[Self]] = None) -> str:
        return cls.__name__

    def repr_rich(self, visited: List[int]) -> str:
        attrs = [(item.name, getattr(self, item.name)) for item in self.__class__._struct_fields]
        if CONFIG["pretty_repr"]:
            body = "\n" + ",\n".join(indent(f"{attr}={field.repr_handler(visited[:])}", "    ") for attr, field in attrs) + "\n"
        else:
            body = ", ".join(f"{attr}={field.repr_handler(visited[:])}" for attr, field in attrs)
        return f"{self.__class__.__name__}({body})"


class _ForwardRoot:
    def __init__(self, *args, **kwargs):
        self.root = None

    def set_root(self, root: 'Struct'):
        self.root = root
