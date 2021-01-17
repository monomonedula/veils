from typing import Optional, Dict, Any


class VeilFactory:
    _proxied_dunders = (
        "__call__",
        "__str__",
        "__bytes__",
        "__format__",
        "__lt__",
        "__le__",
        "__ge__",
        "__gt__",
        "__eq__",
        "__ne__",
        "__bool__",
        "__hash__",
        "__getitem__",
        "__get__",
        "__set__",
        "__contains__",
        "__missing__",
        "__setitem__",
        "__delitem__",
        "__iter__",
        "__len__",
        "__reversed__",
    )

    _naked_dunders = tuple()

    def __init__(self, veil_class, proxied_dunders=None, naked_dunders=None):
        self._veil_class = veil_class
        if proxied_dunders is not None:
            self._proxied_dunders = proxied_dunders
        if naked_dunders is not None:
            self._naked_dunders = naked_dunders

    def veil_of(
        self,
        obj,
        *,
        methods: Optional[Dict[str, Any]] = None,
        async_methods: Optional[Dict[str, Any]] = None,
        props: Optional[Dict[str, Any]] = None,
    ):
        class VeilMeta(type):
            def __new__(mcs, name, bases, dct):
                for method in (
                    attr
                    for attr in dir(obj)
                    if attr in self._proxied_dunders and callable(getattr(obj, attr))
                ):
                    dct[method] = _dunder_proxy(method)
                for method in (
                    attr
                    for attr in dir(obj)
                    if attr in self._naked_dunders and callable(getattr(obj, attr))
                ):
                    dct[method] = _naked_dunder(method)

                return super(VeilMeta, mcs).__new__(mcs, name, bases, dct)

        class _Veil(self._veil_class, metaclass=VeilMeta):
            pass

        return _Veil(obj, methods=methods, async_methods=async_methods, props=props)


def _naked_dunder(name):
    def dunder_wrapper(self, *args, **kwargs):
        return getattr(self._origin, name)(*args, **kwargs)

    return dunder_wrapper


def _dunder_proxy(name):
    def dunder_wrapper(self, *args, **kwargs):
        print("dunder", name)
        return self.__getattr__(name)(*args, **kwargs)

    return dunder_wrapper
