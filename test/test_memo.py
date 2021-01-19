import pytest

from veils.memo import Memo, memo


class Foo:
    def __init__(self):
        self._sum = 0

    def sum(self, a, b):
        self._sum += +a + b
        return self._sum

    async def sub(self, a):
        self._sum -= a
        return self._sum

    async def mul(self, a):
        self._sum *= a
        return self._sum

    def __str__(self):
        return "Foo ({})".format(self._sum)


@pytest.mark.asyncio
@pytest.mark.parametrize("memo_class", [Memo, memo])
async def test_memo_simple(memo_class):
    f = Foo()
    m = memo_class(f, cacheable={"sum", "sub"})
    assert m.sum(40, 2) == 42
    assert await m.sub(2) == 40
    assert m.sum(40, 2) == 42
    assert await m.sub(2) == 40

    assert await m.mul(3) == 120
    assert await m.mul(3) == 360


@pytest.mark.asyncio
def test_memo_magic_methods():
    f = Foo()
    m = memo(f, cacheable={"sum", "__str__"})
    assert str(m) == "Foo (0)"
    assert m.sum(40, 2) == 42
    assert str(m) == "Foo (0)"
    assert str(f) == "Foo (42)"
