# Memhax

A python library for accessing raw python objects and other regions in memory.

## Installation

```bash
$ pip install memhax
```

## Usage

### Read/Write raw memory
```python
from memhax.constants import memory

# Read 4 bytes from address 0x12345678
with memory(0x12345678) as mem:
    data = mem.read(4)
```

### Dump an object's struct
```python
from memhax.cpython.primitives import PyLongObject

num_obj = PyLongObject(id(1234))
print(num_obj.struct_str())

# struct PyLongObject {
#     Py_ssize_t      ob_refcnt;
#     PyTypeObject*   ob_type;
#     Py_ssize_t      ob_size;
#     unsigned int[1] ob_digit;
# }
```


### Read/modify python objects
```python
from memhax.cpython.collections import PyTupleObject

my_tuple = (1, "abc", 3.5)
tuple_obj = PyTupleObject(id(my_tuple))

# Get the tuple's length
print(tuple_obj.ob_size())  # => 3

# Replace an item in the tuple
new_item = [my_tuple, b"123"]
tuple_obj.ob_item[0] = id(new_item)
print(my_tuple)  # => ([(...), b'123'], 'abc', 3.5)
```
