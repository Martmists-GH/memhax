from memhax.cpython.object import PyVarObject, PyObject
from memhax.native import Pointer, DynamicSizeArray, Char
from memhax.proxy import Struct


class PyTupleObject(PyVarObject):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.array("ob_item", lambda _addr: Pointer(_addr, PyObject), self.ob_size)


class PyListObject(PyVarObject):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.pointer("ob_item", lambda _addr: DynamicSizeArray(_addr, lambda _addr2: Pointer(_addr2, PyObject), self.allocated))
        self.ssize_t("allocated")


class PyDictObject(PyObject):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.ssize_t("ma_used")
        self.uint("ma_version_tag_1")
        self.uint("ma_version_tag_2")
        self.pointer("ma_keys", PyDictKeysObject)
        self.pointer("ma_values", lambda _addr: DynamicSizeArray(_addr, lambda _addr2: Pointer(_addr2, PyObject), self.ma_used))


class PyDictKeysObject(Struct):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.ssize_t("dk_refcnt")
        self.ssize_t("dk_size")
        self.pointer("dk_lookup")
        self.ssize_t("dk_usable")
        self.ssize_t("dk_nentries")
        # TODO: dk_entries

        def get_indices_size() -> int:
            size = self.dk_size()
            if size <= 0xff:
                return 1
            elif size <= 0xffff:
                return 2
            elif size <= 0xffffffff:
                return 4
            else:
                return 8

        self.array("dk_indices", Char, get_indices_size)
        # TODO: dk_entries?


class PySetObject(PyObject):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.ssize_t("fill")
        self.ssize_t("used")
        self.ssize_t("mask")
        self.pointer("table", lambda _addr: DynamicSizeArray(_addr, _PySetEntry, self.fill))
        self.ssize_t("hash")
        self.ssize_t("finger")
        self.array("smalltable", _PySetEntry, 8)
        self.pointer("weakreflist", PyObject)


class _PySetEntry(Struct):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.pointer("key", PyObject)
        self.ssize_t("hash")
