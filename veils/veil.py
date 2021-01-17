from inspect import isroutine
from typing import Dict, Any, Optional

from wrapt import ObjectProxy

from veils._async_dummy import async_dummy
from veils.veil_factory import VeilFactory


class Veil:
    __slots__ = ("_origin", "_methods", "_async_methods", "_props", "_pierced")

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
        self._pierced: Bool = Bool(False)

    def __repr__(self):
        return "<{} at 0x{:x} for {} at 0x{:x}>".format(
            type(self).__name__, id(self), type(self._origin).__name__, id(self._origin)
        )

    def __getattribute__(self, attr):
        if attr == "__class__":
            return self._origin.__class__
        return object.__getattribute__(self, attr)

    def __getattr__(self, attr):
        if not self._pierced:
            if attr in self._props:
                return self._props[attr]
            elif attr in self._methods:
                return VeiledMethod(
                    getattr(self._origin, attr),
                    self._methods[attr],
                    self._pierced,
                )
            elif attr in self._async_methods:
                return VeiledAsyncMethod(
                    getattr(self._origin, attr),
                    self._async_methods[attr],
                    self._pierced,
                )
        item = self._origin.__getattribute__(attr)
        if isroutine(item):
            item = VeiledPiercableMethod(item, self._pierced)
        else:
            self._pierced.value = True
        return item


class Bool:
    """
    A class to pass a bool value by reference
    """

    def __init__(self, value: bool):
        self.value = value

    def __bool__(self):
        return self.value


class VeiledMethod(ObjectProxy):
    def __init__(self, wrapped, cached_value: Any, pierced: Bool):
        super(VeiledMethod, self).__init__(wrapped)
        self._self_cached: Any = cached_value
        self._self_pierced: Bool = pierced

    def __call__(self, *args, **kwargs):
        if self._self_pierced:
            return self.__wrapped__(*args, **kwargs)
        return self._self_cached


class VeiledAsyncMethod(ObjectProxy):
    def __init__(self, wrapped, cached_value: Any, pierced: Bool):
        super(VeiledAsyncMethod, self).__init__(wrapped)
        self._self_cached: Any = cached_value
        self._self_pierced: Bool = pierced

    def __call__(self, *args, **kwargs):
        if self._self_pierced:
            return self.__wrapped__(*args, **kwargs)
        return async_dummy(self._self_cached)


class VeiledPiercableMethod(ObjectProxy):
    def __init__(self, wrapped, pierced: Bool):
        super(VeiledPiercableMethod, self).__init__(wrapped)
        self._self_pierced: Bool = pierced

    def __call__(self, *args, **kwargs):
        self._self_pierced.value = True
        return self.__wrapped__(*args, **kwargs)


veil = VeilFactory(Veil).veil_of
