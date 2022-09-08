from memhax.native import NullTerminatedString
from memhax.proxy import Struct


class PyAsyncMethods(Struct):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.pointer("am_await")
        self.pointer("am_aiter")
        self.pointer("am_anext")


class PyNumberMethods(Struct):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.pointer("nb_add")
        self.pointer("nb_subtract")
        self.pointer("nb_multiply")
        self.pointer("nb_remainder")
        self.pointer("nb_divmod")
        self.pointer("nb_power")
        self.pointer("nb_negative")
        self.pointer("nb_positive")
        self.pointer("nb_absolute")
        self.pointer("nb_bool")
        self.pointer("nb_invert")
        self.pointer("nb_lshift")
        self.pointer("nb_rshift")
        self.pointer("nb_and")
        self.pointer("nb_xor")
        self.pointer("nb_or")
        self.pointer("nb_int")
        self.pointer("nb_reserved")
        self.pointer("nb_float")
        self.pointer("nb_inplace_add")
        self.pointer("nb_inplace_subtract")
        self.pointer("nb_inplace_multiply")
        self.pointer("nb_inplace_remainder")
        self.pointer("nb_inplace_power")
        self.pointer("nb_inplace_lshift")
        self.pointer("nb_inplace_rshift")
        self.pointer("nb_inplace_and")
        self.pointer("nb_inplace_xor")
        self.pointer("nb_inplace_or")
        self.pointer("nb_floor_divide")
        self.pointer("nb_true_divide")
        self.pointer("nb_inplace_floor_divide")
        self.pointer("nb_inplace_true_divide")
        self.pointer("nb_index")
        self.pointer("nb_matrix_multiply")
        self.pointer("nb_inplace_matrix_multiply")


class PySequenceMethods(Struct):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.pointer("sq_length")
        self.pointer("sq_concat")
        self.pointer("sq_repeat")
        self.pointer("sq_item")
        self.pointer("was_sq_slice")
        self.pointer("sq_ass_item")
        self.pointer("was_sq_ass_slice")
        self.pointer("sq_contains")
        self.pointer("sq_inplace_concat")
        self.pointer("sq_inplace_repeat")


class PyMappingMethods(Struct):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.pointer("mp_length")
        self.pointer("mp_subscript")
        self.pointer("mp_ass_subscript")


class PyBufferProcs(Struct):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.pointer("bf_getbuffer")
        self.pointer("bf_releasebuffer")
