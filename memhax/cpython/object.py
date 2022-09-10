from __future__ import annotations

from typing import List

from memhax.cpython.type_attributes import PyAsyncMethods, PyNumberMethods, PySequenceMethods, PyMappingMethods, PyBufferProcs, PyMethodDef, PyMemberDef, \
    PyGetSetDef
from memhax.native.structs import Struct
from memhax.native.native import Py_ssize_t, UnsignedInteger
from memhax.native.native_complex import Pointer, NullTerminatedArray, NullTerminatedString


class PyObject(Struct[object]):
    ob_refcnt: Py_ssize_t
    ob_type: Pointer[PyTypeObject]

    def incref(self):
        self.ob_refcnt(self.ob_refcnt() + 1)

    def decref(self):
        self.ob_refcnt(self.ob_refcnt() - 1)

    def _reinterpret(self) -> object:
        from memhax.cpython.collections import PyTupleObject
        tup = (None,)
        _tuple = PyTupleObject(id(tup))
        _tuple.ob_item[0]().decref()
        _tuple.ob_item[0].raw(self.address)
        self.incref()
        return tup[0]

    def get(self) -> object:
        return self._reinterpret()


class PyVarObject(PyObject):
    ob_size: Py_ssize_t


class PyTypeObject(PyVarObject, Struct[type]):
    tp_name: Pointer[NullTerminatedString]
    tp_basicsize: Py_ssize_t
    tp_itemsize: Py_ssize_t
    tp_dealloc: Pointer
    tp_vectorcall_offset: Py_ssize_t
    tp_getattr: Pointer
    tp_setattr: Pointer
    tp_as_async: Pointer[PyAsyncMethods]
    tp_repr: Pointer
    tp_as_number: Pointer[PyNumberMethods]
    tp_as_sequence: Pointer[PySequenceMethods]
    tp_as_mapping: Pointer[PyMappingMethods]
    tp_hash: Pointer
    tp_call: Pointer
    tp_str: Pointer
    tp_getattro: Pointer
    tp_setattro: Pointer
    tp_as_buffer: Pointer[PyBufferProcs]
    tp_flags: Py_ssize_t
    tp_doc: Pointer[NullTerminatedString]
    tp_traverse: Pointer
    tp_clear: Pointer
    tp_richcompare: Pointer
    tp_weaklistoffset: Py_ssize_t
    tp_iter: Pointer
    tp_iternext: Pointer
    tp_methods: Pointer[NullTerminatedArray[PyMethodDef]]
    tp_members: Pointer[NullTerminatedArray[PyMemberDef]]
    tp_getset: Pointer[NullTerminatedArray[PyGetSetDef]]
    tp_base: Pointer[PyTypeObject]
    tp_dict: Pointer[PyObject]
    tp_descr_get: Pointer
    tp_descr_set: Pointer
    tp_dictoffset: Py_ssize_t
    tp_init: Pointer
    tp_alloc: Pointer
    tp_new: Pointer
    tp_free: Pointer
    tp_is_gc: Pointer
    tp_bases: Pointer[PyObject]
    tp_mro: Pointer[PyObject]
    tp_cache: Pointer
    tp_subclasses: Pointer
    tp_weaklist: Pointer
    tp_del: Pointer
    tp_version_tag: UnsignedInteger
    tp_finalize: Pointer
    tp_vectorcall: Pointer

    def repr_simple(self, visited: List[int]) -> str:
        return repr(self.get())
