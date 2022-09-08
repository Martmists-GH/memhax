from memhax.cpython.primitives import PyUnicodeObject, PyLongObject, PyASCIIObject, PyCompactUnicodeObject
from memhax.cpython.collections import PyTupleObject, PyListObject


def main():
    x = (1, 2, 3)
    x_repr = PyTupleObject(id(x))
    x_repr.ob_item[2] = id(9999)
    print(x_repr)
    print(x)
    num_repr = PyLongObject(x_repr.ob_item[2].raw())
    print(num_repr)
    num_repr.ob_digit[0] = 123456
    print(x)
    print(9999)
    s = "s2\u202eend"
    s_obj = PyUnicodeObject(id(s))
    print(s_obj)
    print(s_obj.value())


if __name__ == "__main__":
    main()
