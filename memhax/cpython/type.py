from memhax.native import NullTerminatedString
from memhax.proxy import Struct


class PyMethodDef(Struct):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.pointer("ml_name", NullTerminatedString)
        self.pointer("ml_meth")
        self.int("ml_flags")
        self.pointer("ml_doc", NullTerminatedString)


class PyMemberDef(Struct):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.pointer("name", NullTerminatedString)
        self.int("type")
        self.ssize_t("offset")
        self.int("flags")
        self.pointer("doc", NullTerminatedString)


class PyGetSetDef(Struct):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.pointer("name", NullTerminatedString)
        self.pointer("get")
        self.pointer("set")
        self.pointer("doc", NullTerminatedString)
        self.pointer("closure")
