from typing import Optional, Dict, Any

from wrapt import ObjectProxy

from veil._async_dummy import async_dummy
from veil.veil import Bool


class Unpiercable:
    __slots__ = (
        "_origin",
        "_methods",
        "_async_methods",
        "_props",
    )

    def __init__(
        self,
        wrapped,
        *,
        methods: Optional[Dict[str, Any]] = None,
        async_methods: Optional[Dict[str, Any]] = None,
        props: Optional[Dict[str, Any]] = None,
    ):
        self._origin = wrapped
        self._methods = {} if methods is None else methods
        self._async_methods = {} if async_methods is None else async_methods
        self._props = {} if props is None else props

    def __getattribute__(self, attr):
        if attr == "__class__":
            return self._origin.__class__
        return object.__getattribute__(self, attr)

    def __getattr__(self, attr):
        if attr in self._props:
            return self._props[attr]
        elif attr in self._methods:
            return CachedMethod(getattr(self._origin, attr), self._methods[attr])
        elif attr in self._async_methods:
            return CachedAsyncMethod(
                getattr(self._origin, attr), self._async_methods[attr]
            )

        return getattr(self._origin, attr)


class CachedMethod(ObjectProxy):
    def __init__(self, wrapped, cached: Any):
        super(CachedMethod, self).__init__(wrapped)
        self._self_cached: Any = cached

    def __call__(self, *args, **kwargs):
        return self._self_cached


class CachedAsyncMethod(ObjectProxy):
    def __init__(self, wrapped, cached_value: Any):
        super(CachedAsyncMethod, self).__init__(wrapped)
        self._self_cached: Any = cached_value

    def __call__(self, *args, **kwargs):
        return async_dummy(self._self_cached)
