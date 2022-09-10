import atexit
from contextlib import contextmanager
from typing import get_args, Any, Optional, Tuple


_MEMORY = open("/proc/self/mem", "r+b")
CONFIG = {
    "simplified_repr": True,
    "pretty_repr": True,
    "hide_pointers_repr": True,
}
__all__ = ("CONFIG", "memory", "instance_type_args")


def instance_type_args(instance: Any) -> Optional[Tuple[Any, ...]]:
    _orig = getattr(instance, "__orig_class__", None)
    if _orig is None:
        return None
    return get_args(_orig)


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
