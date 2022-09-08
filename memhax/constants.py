import atexit
from contextlib import contextmanager
from typing import Optional

_MEMORY = open("/proc/self/mem", "r+b")
CONFIG = {
    "expand_types": False,
    "hide_pointers": True,
    "pretty_print": True,
}
__all__ = ("CONFIG", "memory")


@contextmanager
def memory(address: Optional[int] = None):
    tmp = _MEMORY.tell()
    if address is not None:
        _MEMORY.seek(address)
    yield _MEMORY
    _MEMORY.seek(tmp)


@atexit.register
def __close_memory():
    _MEMORY.close()
