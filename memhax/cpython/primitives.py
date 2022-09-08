from ctypes import c_wchar, sizeof
from struct import unpack

from memhax.constants import memory
from memhax.cpython.object import PyObject, PyVarObject
from memhax.native import Byte, UnsignedInteger


class PyASCIIObject(PyObject):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.ssize_t("length")
        self.ssize_t("hash")
        self.uint("state")
        self.pointer("wstr")

    def _string(self, interned, kind, compact, ascii, ready):
        if not (kind == 1 and compact and ascii and ready):
            raise ValueError("Not a PyASCIIObject valid string:", interned, kind, compact, ascii, ready)
        addr = self.address + self.offsetafter(self.wstr)
        with memory(addr) as mem:
            data = mem.read(self.length())
            return data.decode("ascii")

    def value(self) -> str:
        state = self.state()
        interned = state & 0b11
        kind = (state >> 2) & 0b111
        compact = (state >> 5) & 0b1
        ascii = (state >> 6) & 0b1
        ready = (state >> 7) & 0b1
        return self._string(interned, kind, compact, ascii, ready)


class PyCompactUnicodeObject(PyASCIIObject):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.ssize_t("utf8_length")
        self.pointer("utf8")
        self.ssize_t("wstr_length")

    def _string(self, interned, kind, compact, ascii, ready):
        if kind == 1 and compact and ascii and ready:
            return super()._string(interned, kind, compact, ascii, ready)
        if kind != 0 and compact and not ascii and ready:
            addr = self.address + self.offsetafter(self.wstr_length)
            with memory(addr) as mem:
                data = mem.read(self.length() * kind)
                fmt = {
                    1: "utf-8",
                    2: "utf-16",
                    4: "utf-32"
                }
                return data.decode(fmt[kind])
        raise ValueError("Not a PyCompactUnicodeObject valid string:", interned, kind, compact, ascii, ready)


class PyUnicodeObject(PyCompactUnicodeObject):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.pointer("data")

    def _string(self, interned, kind, compact, ascii, ready):
        if kind == 1 and compact and ascii and ready:
            return super()._string(interned, kind, compact, ascii, ready)  # PyASCIIObject
        if kind != 0 and compact and not ascii and ready:
            return super()._string(interned, kind, compact, ascii, ready)  # PyCompactUnicodeObject
        if kind == 0 and not compact and not ascii and not ready:
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
        raise ValueError("Not a PyUnicodeObject valid string:", interned, kind, compact, ascii, ready)


class PyBytesObject(PyVarObject):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.ssize_t("ob_shash")
        self.array("ob_sval", Byte, self.ob_size)


class PyLongObject(PyVarObject):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.array("ob_digit", UnsignedInteger, lambda: abs(self.ob_size()))


class PyFloatObject(PyObject):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.double("ob_fval")
