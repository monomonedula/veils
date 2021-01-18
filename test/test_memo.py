import pytest

from veils.memo import Memo


class Foo:
    def __init__(self):
        self._sum = 0

    def sum(self, a, b):
        self._sum += + a + b
        return self._sum

    async def sub(self, a):
        self._sum -= a
        return self._sum

    async def mul(self, a):
        self._sum *= a
        return self._sum


@pytest.mark.asyncio
async def test_memo_simple():
    f = Foo()
    m = Memo(f, cacheable={"sum", "sub"})
    assert m.sum(40, 2) == 42
    assert await m.sub(2) == 40
    assert m.sum(40, 2) == 42
    assert await m.sub(2) == 40

    assert await m.mul(3) == 120
    assert await m.mul(3) == 360
