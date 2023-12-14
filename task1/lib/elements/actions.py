import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Union, NoReturn, Dict, Any, TypeVar, Callable

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

TypeElement = TypeVar('TypeElement', bound='Element')  # any subclass of Element


class IncompleteListActionError(Exception):
    pass


class Action(ABC):
    """Base abstract class for actions."""

    __slots__ = "_owner", "debug_value"

    def __init__(self, owner: TypeElement) -> None:
        self._owner: TypeElement = owner
        self.debug_value: Optional[Any] = None  # return value of the __call__ method, for logging and debugging

    @abstractmethod
    def __call__(self):
        pass

    def _continuable_read_list_action(self, method_name: str, *args) -> Any:
        elements = self._owner.web_element if isinstance(self._owner.web_element, list) else [self._owner.web_element]
        if self._owner.start_index >= len(elements):
            # new elements list lesser than was previous
            # read values from beginning of list
            start_index = 0
            self.debug_value = []
        else:
            # continue read values from list
            start_index = self._owner.start_index
            self.debug_value = self._owner.incomplete_result

        for index, elm in enumerate(elements):
            # skip values that were already read
            if index < start_index:
                continue

            try:
                attr = getattr(elm, method_name)
                if isinstance(attr, Callable):
                    # method
                    self.debug_value.append(attr(*args))
                else:
                    # property
                    self.debug_value.append(attr)
            except (NoSuchElementException, StaleElementReferenceException) as err:
                # save incomplete list and index to Element - for using these values in next reading attempt
                self._owner.start_index = index
                self._owner.incomplete_result = self.debug_value
                raise IncompleteListActionError(f"{index=} {self.debug_value=} {err}")
        return self.debug_value


class ClearAction(Action):
    """Clear content of web page element.
    self._owner.web_element is the WebElement
    returns None
    """

    def __call__(self) -> None:
        self._owner.web_element.clear()


class SendKeysAction(Action):
    """Sends string value to element.
    element is the WebElement
    value is string to send
    returns None
    """

    def __init__(self, owner: TypeElement, value: str) -> None:
        super().__init__(owner)
        self._value = value

    def __call__(self) -> None:
        self._owner.web_element.send_keys(self._value)


class ReadTextAction(Action):
    """Reads element's text.
    self._owner.web_element is the WebElement
    returns the WebElement. text result
    """

    def __call__(self) -> str:
        self.debug_value = self._owner.web_element.text
        return self.debug_value
