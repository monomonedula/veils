from inspect import iscoroutinefunction
from typing import Collection, MutableMapping, Callable

from cachetools.keys import hashkey
from typing_extensions import Protocol


from cachetools import LRUCache
from wrapt import ObjectProxy

from veils.veil_factory import VeilFactory


class Key(Protocol):
    def __call__(self, *args, **kwargs) -> tuple:
        ...


class Memo:
    __slots__ = (
        "_origin",
        "__cacheable",
        "__cached",
        "__key",
        "__new_cache",
    )

    def __init__(
        self,
        wrapped,
        *,
        cacheable: Collection[str] = None,
        cache: Callable[[], MutableMapping] = lambda: LRUCache(maxsize=128),
        key: Key = hashkey
    ):
        self._origin = wrapped
        self.__cacheable = cacheable
        self.__new_cache = cache
        self.__key = key
        self.__cached = {}

    def __repr__(self):
        return "<{} at 0x{:x} for {} at 0x{:x}>".format(
            type(self).__name__, id(self), type(self._origin).__name__, id(self._origin)
        )

    def __getattribute__(self, attr):
        if attr == "__class__":
            return self._origin.__class__
        return object.__getattribute__(self, attr)

    def __getattr__(self, item):
        if item in self.__cacheable:
            if item not in self.__cached:
                attr = getattr(self._origin, item)
                if callable(attr):
                    if iscoroutinefunction(attr):
                        self.__cached[item] = MemoizedAsyncMethod(
                            attr,
                            self.__new_cache(),
                            self.__key,
                        )
                    else:
                        self.__cached[item] = MemoizedMethod(
                            attr,
                            self.__new_cache(),
                            self.__key,
                        )
                else:
                    self.__cached[item] = attr
            return self.__cached[item]
        return getattr(self._origin, item)


class MemoizedMethod(ObjectProxy):
    def __init__(self, method, cache: MutableMapping, key: Key):
        super(MemoizedMethod, self).__init__(method)
        self._self_cache = cache
        self._self_key = key

    def __call__(self, *args, **kwargs):
        k = self._self_key(*args, **kwargs)
        try:
            return self._self_cache[k]
        except KeyError:
            pass
        v = self.__wrapped__(*args, **kwargs)
        try:
            self._self_cache[k] = v
        except ValueError:
            pass  # value too large
        return v


class MemoizedAsyncMethod(ObjectProxy):
    def __init__(self, method, cache: MutableMapping, key: Key):
        super(MemoizedAsyncMethod, self).__init__(method)
        self._self_cache = cache
        self._self_key = key

    async def __call__(self, *args, **kwargs):
        k = self._self_key(*args, **kwargs)
        try:
            return self._self_cache[k]
        except KeyError:
            pass
        v = await self.__wrapped__(*args, **kwargs)
        try:
            self._self_cache[k] = v
        except ValueError:
            pass  # value too large
        return v


_veil_factory = VeilFactory(Memo)


def memo(
    wrapped,
    *,
    cacheable: Collection[str] = None,
    cache: Callable[[], MutableMapping] = lambda: LRUCache(maxsize=128),
    key: Key = hashkey
):
    return _veil_factory.veil_of(wrapped, cacheable=cacheable, cache=cache, key=key)
