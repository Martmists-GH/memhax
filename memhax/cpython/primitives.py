from ctypes import sizeof, c_wchar

from memhax.utils import memory
from memhax.cpython.object import PyVarObject, PyObject
from memhax.native.native import Double, Py_ssize_t, Char
from memhax.native.native_complex import PropertySizeArray, Pointer
from memhax.native.native_size import uint32_t
from memhax.native.structs import Struct


class PyLongObject(PyVarObject, Struct[int]):
    ob_digit: PropertySizeArray[uint32_t, lambda self: abs(self.ob_size())]


class PyFloatObject(PyVarObject, Struct[float]):
    ob_fval: Double


class PyBytesObject(PyVarObject, Struct[bytes]):
    ob_shash: Py_ssize_t
    ob_sval: PropertySizeArray[Char, lambda self: self.ob_size()]


class PyASCIIObject(PyObject, Struct[str]):
    length: Py_ssize_t
    hash: Py_ssize_t
    state: uint32_t
    wstr: Pointer

    def _string(self, interned: int, kind: int, compact: bool, _ascii: bool, ready: bool) -> str:
        if not (kind == 1 and compact and _ascii and ready):
            raise ValueError("Not a PyASCIIObject valid string:", interned, kind, compact, _ascii, ready)
        addr = self.address + PyASCIIObject.offset_after(self.wstr)
        with memory(addr) as mem:
            data = mem.read(self.length())
            return data.decode("ascii")

    def value(self) -> str:
        state = self.state()
        interned = state & 0b11
        kind = (state >> 2) & 0b111
        compact = (state >> 5) & 0b1
        _ascii = (state >> 6) & 0b1
        ready = (state >> 7) & 0b1
        return self._string(interned, kind, compact, _ascii, ready)


class PyCompactUnicodeObject(PyASCIIObject):
    utf8_length: Py_ssize_t
    utf8: Pointer
    wstr_length: Py_ssize_t

    def _string(self, interned: int, kind: int, compact: bool, _ascii: bool, ready: bool) -> str:
        if kind == 1 and compact and _ascii and ready:
            return super()._string(interned, kind, compact, _ascii, ready)
        if kind != 0 and compact and not _ascii and ready:
            addr = self.address + PyCompactUnicodeObject.offset_after(PyCompactUnicodeObject.wstr_length)
            with memory(addr) as mem:
                data = mem.read(self.length() * kind)
                fmt = {
                    1: "utf-8",
                    2: "utf-16",
                    4: "utf-32"
                }
                return data.decode(fmt[kind])
        raise ValueError("Not a PyCompactUnicodeObject valid string:", interned, kind, compact, _ascii, ready)


class PyUnicodeObject(PyCompactUnicodeObject):
    data: Pointer

    def _string(self, interned: int, kind: int, compact: bool, _ascii: bool, ready: bool) -> str:
        if kind == 1 and compact and _ascii and ready:
            return super()._string(interned, kind, compact, _ascii, ready)  # PyASCIIObject
        if kind != 0 and compact and not _ascii and ready:
            return super()._string(interned, kind, compact, _ascii, ready)  # PyCompactUnicodeObject
        if kind == 0 and not compact and not _ascii and not ready:
            with memory(self.wstr()) as mem:
                data = mem.read(self.wstr_length() * sizeof(c_wchar))  # Depends on ctypes :(
                fmt = {
                    2: "utf-16",
                    4: "utf-32"
                }
                return data.decode(fmt[sizeof(c_wchar)])
        elif kind != 0 and not compact and ready:
            with memory(self.data()) as mem:
                data = mem.read(self.length() * kind)
                fmt = {
                    1: "utf-8",
                    2: "utf-16",
                    4: "utf-32"
                }
                return data.decode(fmt[kind])
        raise ValueError("Not a PyUnicodeObject valid string:", interned, kind, compact, _ascii, ready)
