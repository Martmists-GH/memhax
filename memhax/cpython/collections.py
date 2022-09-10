from memhax.cpython.object import PyVarObject, PyObject
from memhax.native.native import Py_ssize_t
from memhax.native.native_complex import PropertySizeArray, Pointer, StaticSizeArray
from memhax.native.native_size import uint64_t
from memhax.native.structs import Struct


class PyTupleObject(PyVarObject, Struct[tuple]):
    ob_item: PropertySizeArray[Pointer[PyObject], lambda self: self.ob_size()]  # how am I gonna pass `self` [PyTupleObject] to this function


class PyListObject(PyVarObject, Struct[list]):
    ob_item: Pointer[PropertySizeArray[Pointer[PyObject], lambda self: self.allocated()]]
    allocated: Py_ssize_t


class _PySetEntry(Struct[None]):
    key: Pointer[PyObject]
    hash: Py_ssize_t


class PySetObject(PyObject, Struct[set]):
    fill: Py_ssize_t
    used: Py_ssize_t
    mask: Py_ssize_t
    table: Pointer[PropertySizeArray[_PySetEntry, lambda self: self.fill()]]
    hash: Py_ssize_t
    finger: Py_ssize_t
    smalltable: StaticSizeArray[_PySetEntry, 8]
    weakreflist: Pointer[PyObject]


class PyDictObject(PyObject, Struct[dict]):
    ma_used: Py_ssize_t
    ma_version_tag: uint64_t
    # TODO: PyDictKeysObject; It's a fairly complex struct so not implemented yet
    ma_keys: Pointer
    ma_values: Pointer[PropertySizeArray[Pointer[PyObject], lambda self: self.ma_used()]]
