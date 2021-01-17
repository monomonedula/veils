# Veil
[![EO principles respected here](https://www.elegantobjects.org/badge.svg)](https://www.elegantobjects.org)
[![Build Status](https://travis-ci.org/monomonedula/veil.svg?branch=main)](https://travis-ci.org/monomonedula/veil)
[![codecov](https://codecov.io/gh/monomonedula/veil/branch/main/graph/badge.svg)](https://codecov.io/gh/monomonedula/veil)
[![PyPI version](https://badge.fury.io/py/veil.svg)](https://badge.fury.io/py/veil)

`veil` is a python implementation of a ruby [veils package](https://github.com/yegor256/veils).
Long story short, it provides convenient object decorators for data memoization.



## Installation

`pip install veils`

## Usage

```python
from veils import veil

obj = veil(
    obj,
    methods={"__str__": "hello, world!", "foo": "42"}
)
str(obj)  # returns "hello, world!"
obj.foo()  # returns "42"
```

The methods `__str__` and `foo` will return "Hello, world!" and "42" respectively
until some other method is called and the veil is "pierced".

You can also use `unpiercable` decorator, which will never be pierced: a very good instrument for data memoization.

And it works the same way for asynchronous methods too

```python
obj = veil(
    obj,
    async_methods={"foo": "42"}
)
await obj.foo()     # returns "42"
```

And also for properties
```python
obj = veil(
    obj,
    props={"bar": "42"}
)

obj.bar     # equals "42"
```




## Advanced usage

The python implementations of veil is somewhat tricky due to the magic methods which
are being accessed bypassing the `__getattribute__` method.
Therefore, this implementation, in this particular case, relies on metaclasses in order to define magic methods on the fly in the veil object so that they correspond to those defined in the object being wrapped.

`veil` and `unpiercable` are just shortcuts to `VeilFactory(Veil).veil_of` and `VeilFactory(Unpiercable).veil_of`.

In some advanced cases you may want a different list of magic methods to be transparent or proxied by a veil object. In oder to obtain such behavior
you may create a custom veil factory like so: `VeilFactory(Veil, proxied_dunders, naked_dunders)`. 
`naked_dunders` is a list of methods bypassing the veil.
`proxied_dunders` is a list of methods to be veiled.
