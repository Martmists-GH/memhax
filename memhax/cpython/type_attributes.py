from memhax.native.native import Integer, Py_ssize_t
from memhax.native.native_complex import Pointer, NullTerminatedString
from memhax.native.structs import Struct


class PyAsyncMethods(Struct[None]):
    am_await: Pointer
    am_aiter: Pointer
    am_anext: Pointer
    am_send: Pointer


class PyNumberMethods(Struct[None]):
    nb_add: Pointer
    nb_subtract: Pointer
    nb_multiply: Pointer
    nb_remainder: Pointer
    nb_divmod: Pointer
    nb_power: Pointer
    nb_negative: Pointer
    nb_positive: Pointer
    nb_absolute: Pointer
    nb_bool: Pointer
    nb_invert: Pointer
    nb_lshift: Pointer
    nb_rshift: Pointer
    nb_and: Pointer
    nb_xor: Pointer
    nb_or: Pointer
    nb_int: Pointer
    nb_reserved: Pointer
    nb_float: Pointer
    nb_inplace_add: Pointer
    nb_inplace_subtract: Pointer
    nb_inplace_multiply: Pointer
    nb_inplace_remainder: Pointer
    nb_inplace_power: Pointer
    nb_inplace_lshift: Pointer
    nb_inplace_rshift: Pointer
    nb_inplace_and: Pointer
    nb_inplace_xor: Pointer
    nb_inplace_or: Pointer
    nb_floor_divide: Pointer
    nb_true_divide: Pointer
    nb_inplace_floor_divide: Pointer
    nb_inplace_true_divide: Pointer
    nb_index: Pointer
    nb_matrix_multiply: Pointer
    nb_inplace_matrix_multiply: Pointer


class PySequenceMethods(Struct[None]):
    sq_length: Pointer
    sq_concat: Pointer
    sq_repeat: Pointer
    sq_item: Pointer
    was_sq_slice: Pointer
    sq_ass_item: Pointer
    was_sq_ass_slice: Pointer
    sq_contains: Pointer
    sq_inplace_concat: Pointer
    sq_inplace_repeat: Pointer


class PyMappingMethods(Struct[None]):
    mp_length: Pointer
    mp_subscript: Pointer
    mp_ass_subscript: Pointer


class PyBufferProcs(Struct[None]):
    bf_getbuffer: Pointer
    bf_releasebuffer: Pointer


class PyMethodDef(Struct[None]):
    ml_name: Pointer[NullTerminatedString]
    ml_meth: Pointer
    ml_flags: Integer
    ml_doc: Pointer[NullTerminatedString]


class PyMemberDef(Struct[None]):
    name: Pointer[NullTerminatedString]
    type: Integer
    offset: Py_ssize_t
    flags: Integer
    doc: Pointer[NullTerminatedString]


class PyGetSetDef(Struct[None]):
    name: Pointer[NullTerminatedString]
    get: Pointer
    set: Pointer
    doc: Pointer[NullTerminatedString]
    closure: Pointer
