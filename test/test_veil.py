from unittest.mock import Mock

import pytest

from veil.veil import Veil
from veil.unpiercable import Unpiercable


class Foo:
    def __init__(self):
        self._bar_call_count = 0
        self.prop1 = "Property 1"
        self.prop2 = "Property 2"

    def bar(self):
        return 42

    def baz(self, name):
        return "hello {}".format(name)

    def foo(self, *args, **kwargs):
        return ", ".join(map(str, [*args, kwargs]))

    async def greet_async(self, name):
        return "Asynchronous hello to {}!".format(name)

    async def dummy_async(self):
        return "Dummy async method"


def test_veil_piercing():
    """
    Should pierce after calling a method that is not cached
    """
    veiled = Veil(Foo(), methods={"bar": 69})
    for _ in range(10):
        assert veiled.bar() == 69

    assert veiled.baz("Donald") == "hello Donald"
    assert veiled.bar() == 42


def test_veild_piercing_async():
    """
    Should pierce after calling an async method that is not cached
    """
    veiled = Veil(Foo(), methods={"bar": 69})
    for _ in range(10):
        assert veiled.bar() == 69

    assert veiled.baz("Donald") == "hello Donald"
    assert veiled.bar() == 42


def test_veil_piercing_prop():
    """
    Should pierce after accessing a property that is not cached
    """
    veiled = Veil(Foo(), methods={"bar": 69}, props={"prop1": "Cached prop1"})
    assert veiled.prop1 == "Cached prop1"
    assert veiled.bar() == 69
    assert veiled.prop2 == "Property 2"
    assert veiled.prop1 == "Property 1"


@pytest.mark.asyncio
@pytest.mark.parametrize("veil_class", [Veil, Unpiercable])
async def test_veil_simple_with_args(veil_class):
    veiled = veil_class(
        Foo(),
        methods={"bar": 69, "baz": "Don't care! Veiled!"},
        async_methods={"greet_async": "Cached greet async"},
        props={"prop1": "Veiled prop1!", "prop2": "Veiled prop2!"},
    )
    assert veiled.bar() == 69
    assert veiled.baz("Donald") == "Don't care! Veiled!"
    assert await veiled.greet_async("Donald") == "Cached greet async"
    assert (
        veiled.foo("Some", "Args", keyword_args="Too")
        == "Some, Args, {'keyword_args': 'Too'}"
    )


@pytest.mark.parametrize("veil_class", [Veil, Unpiercable])
def test_veil_isinstance(veil_class):
    assert isinstance(veil_class(Foo()), Foo)


@pytest.mark.asyncio
async def test_unpiercable():
    """
    Should not get pierced even after accessing any property or method
    """
    veiled = Unpiercable(
        Foo(),
        methods={"bar": 69},
        async_methods={"dummy_async": "Decorated dummy"},
        props={"prop1": "Cached prop1"},
    )

    assert veiled.bar() == 69
    assert veiled.baz("Donald") == "hello Donald"
    assert veiled.bar() == 69
    assert veiled.prop2 == "Property 2"
    assert veiled.prop1 == "Cached prop1"
    assert await veiled.greet_async("Donald") == "Asynchronous hello to Donald!"
    assert await veiled.dummy_async() == "Decorated dummy"


@pytest.mark.asyncio
@pytest.mark.parametrize("veil_class", [Veil, Unpiercable])
async def test_not_calling_decorated(veil_class):
    mock = Mock()
    veiled = veil_class(
        mock,
        methods={"bar": 69},
        async_methods={"dummy_async": "Decorated dummy"},
    )
    assert veiled.bar() == 69
    assert await veiled.dummy_async() == "Decorated dummy"
    mock.bar.assert_not_called()
    mock.dummy_async.assert_not_called()
