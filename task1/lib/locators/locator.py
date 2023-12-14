from typing import Any, Tuple, Union, NoReturn
from ..by_type import ByType


class Locator:
    __slots__ = "_by", "_locator"

    def __init__(self, locator: str, by: str = ByType.XPATH) -> None:
        self._by: str = by
        self._locator: str = locator

    def __call__(self, *args, **kwargs) -> Tuple[str, str]:
        # return tuple(by, locator) with formatted string literals
        return self._by, self._locator.format(*args, **kwargs)

    def __get__(self, instance: Any, owner: Any) -> Union[Tuple[str, str], NoReturn]:
        try:
            # return tuple(by, locator) when no formatted string literals
            return self._by, self._locator.format()
        except (IndexError, KeyError):
            # return itself when executed from __call__ method
            return self

    def __repr__(self) -> str:
        return f'Locator(by={self._by}, "{self._locator}")'

    def __str__(self) -> str:
        return self.__repr__()
