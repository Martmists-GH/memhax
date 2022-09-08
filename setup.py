from setuptools import setup

with open("README.md", "r") as fp:
    long_description = fp.read()

try:
    file = open("/proc/self/mem", "r+b", buffering=0)
    file.close()
except FileNotFoundError:
    raise RuntimeError("This package requires access to /proc/self/mem, which does not exist on this system.")

setup(
    name="memhax",
    version="0.0.1",
    packages=['memhax', 'memhax.cpython'],
    description="A Python library for getting access to raw memory and internals",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.9,<3.10',  # TODO: Support other python versions in code
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Operating System :: Unix",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Typing :: Typed",
    ],
)
