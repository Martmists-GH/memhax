from typing import List

from memhax.constants import CONFIG
from memhax.cpython.methods import PyAsyncMethods, PyNumberMethods, PySequenceMethods, PyMappingMethods, PyBufferProcs
from memhax.cpython.type import PyMemberDef, PyGetSetDef, PyMethodDef
from memhax.native import NullTerminatedString, NullTerminatedArray
from memhax.proxy import Struct


class PyObject(Struct):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.ssize_t("ob_refcnt")
        self.pointer("ob_type", PyTypeObject)

    def incref(self) -> int:
        return self.ob_refcnt(self.ob_refcnt() + 1)

    def decref(self) -> int:
        return self.ob_refcnt(self.ob_refcnt() - 1)


class PyVarObject(PyObject):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.ssize_t("ob_size")


class PyTypeObject(PyVarObject):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.pointer("tp_name", NullTerminatedString)
        self.ssize_t("tp_basicsize")
        self.ssize_t("tp_itemsize")
        self.pointer("tp_dealloc")
        self.ssize_t("tp_vectorcall_offset")
        self.pointer("tp_getattr")
        self.pointer("tp_setattr")
        self.pointer("tp_as_async", PyAsyncMethods)
        self.pointer("tp_repr")
        self.pointer("tp_as_number", PyNumberMethods)
        self.pointer("tp_as_sequence", PySequenceMethods)
        self.pointer("tp_as_mapping", PyMappingMethods)
        self.pointer("tp_hash")
        self.pointer("tp_call")
        self.pointer("tp_str")
        self.pointer("tp_getattro")
        self.pointer("tp_setattro")
        self.pointer("tp_as_buffer", PyBufferProcs)
        self.ulong("tp_flags")
        self.pointer("tp_doc", NullTerminatedString)
        self.pointer("tp_traverse")
        self.pointer("tp_clear")
        self.pointer("tp_richcompare")
        self.ssize_t("tp_weaklistoffset")
        self.pointer("tp_iter")
        self.pointer("tp_iternext")
        self.pointer("tp_methods", lambda _addr: NullTerminatedArray(_addr, PyMethodDef))
        self.pointer("tp_members", lambda _addr: NullTerminatedArray(_addr, PyMemberDef))
        self.pointer("tp_getset", lambda _addr: NullTerminatedArray(_addr, PyGetSetDef))
        self.pointer("tp_base", PyTypeObject)
        self.pointer("tp_dict", PyObject)
        self.pointer("tp_descr_get")
        self.pointer("tp_descr_set")
        self.ssize_t("tp_dictoffset")
        self.pointer("tp_init")
        self.pointer("tp_alloc")
        self.pointer("tp_new")
        self.pointer("tp_free")
        self.pointer("tp_is_gc")
        self.pointer("tp_bases", PyObject)
        self.pointer("tp_mro", PyObject)
        self.pointer("tp_cache")
        self.pointer("tp_subclasses")
        self.pointer("tp_weaklist")
        self.pointer("tp_del")
        self.uint("tp_version_tag")
        self.pointer("tp_finalize")
        self.pointer("tp_vectorcall")

    def rich_str(self, objs: List[int] = None) -> str:
        if CONFIG["expand_types"]:
            return super().rich_str(objs)
        return f"<type {self.tp_name()}>"
