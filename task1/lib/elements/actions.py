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


class ClickAction(Action):
    """Clicks by web page element.
    self._owner.web_element is the WebElement
    returns None
    """

    def __call__(self) -> None:
        self._owner.web_element.click()


class IsOnPageAction(Action):
    """Check is element on page.
    self._owner.web_element is the WebElement
    returns bool
    """

    def __call__(self) -> bool:
        self.debug_value = self._owner.web_element
        return self.debug_value is not None


class GetLenAction(Action):
    """Get self._element length.
    self._owner.web_element is the WebElement
    returns int
    """

    def __call__(self) -> int:
        elements = self._owner.web_element if isinstance(self._owner.web_element, list) else [self._owner.web_element]
        self.debug_value = len(elements)
        return self.debug_value


class WaitTextAction(Action):
    """Wait expected text (self._value) appears on element.
       If expected text is None - wait not empty text.
    """
    __slots__ = "_value"

    def __init__(self, owner: TypeElement, value: Optional[str]) -> None:
        super().__init__(owner)
        self._value = value

    def __call__(self) -> bool:
        self.debug_value = self._owner.web_element.text
        logging.debug(f"element.text: '{self.debug_value}'")
        if ((self._value is None and self.debug_value)
                or (self._value is not None and self.debug_value == self._value)):
            return True
        else:
            raise NoSuchElementException


class IsSelectedAction(Action):
    """Check is element(checkbox) selected.
    self._owner.web_element is the WebElement
    returns bool
    """

    def __call__(self) -> bool:
        self.debug_value = self._owner.web_element.is_selected()
        return self.debug_value


class ReadTextListAction(Action):
    """This class works in a pair with Elements class. Reads text from every
    element in self._owner.web_element list.
    self._owner.web_element is the List[WebElement] - result of class Elements
    returns the list of text strings
    """

    def __call__(self) -> List[str]:
        return self._continuable_read_list_action("text")


class GetAttributeAction(Action):
    """Reads attribute value from element.
    self._owner.web_element is the WebElement
    attr_name is name of WebElement's attribute
    returns value of attribute or None if attribute not present
    """

    def __init__(self, owner: TypeElement, attr_name: str) -> None:
        super().__init__(owner)
        self._attr_name = attr_name

    def __call__(self) -> Optional[str]:
        self.debug_value = self._owner.web_element.get_attribute(self._attr_name)
        return self.debug_value


class GetPropertyAction(Action):
    """Reads DOM Property value from element.
    self._owner.web_element is the WebElement
    attr_name is name of WebElement's attribute
    returns value of attribute or None if attribute not present
    """
    __slots__ = "_prop_name"

    def __init__(self, owner: TypeElement, prop_name: str) -> None:
        super().__init__(owner)
        self._prop_name = prop_name

    def __call__(self) -> Optional[str]:
        self.debug_value = self._owner.web_element.get_property(self._prop_name)
        return self.debug_value


class ReadPropertyListAction(Action):
    """This class works in a pair with Elements class. Reads property 'prop_name'
    from every element in self._owner.web_element list.
    self._owner.web_element is the List[WebElement] - result of class Elements
    returns the list of text strings
    """
    __slots__ = "_prop_name"

    def __init__(self, owner: TypeElement, prop_name: str) -> None:
        super().__init__(owner)
        self._prop_name = prop_name

    def __call__(self) -> List[str]:
        return self._continuable_read_list_action("get_property", self._prop_name)


class ReadAttributeListAction(Action):
    """This class works in a pair with Elements class. Reads attribute 'attr_name'
    from every element in self._owner.web_element list.
    self._owner.web_element is the List[WebElement] - result of class Elements
    returns the list of text strings
    """
    __slots__ = "_attr_name"

    def __init__(self, owner: TypeElement, attr_name: str) -> None:
        super().__init__(owner)
        self._attr_name = attr_name

    def __call__(self) -> List[str]:
        return self._continuable_read_list_action("get_attribute", self._attr_name)


class ClickByIndexElementsAction(Action):
    """This class works in a pair with Elements class. Clicks by web page element by index.
    self._owner.web_element is the List[WebElement] - result of class Elements
    returns None
    """
    __slots__ = "_index"

    def __init__(self, owner: TypeElement, index: int) -> None:
        super().__init__(owner)
        self._index = index

    def __call__(self) -> None:
        elements = self._owner.web_element if isinstance(self._owner.web_element, list) else [self._owner.web_element]
        elements[self._index].click()


class IsSelectedByIndexElementsAction(Action):
    """This class works in a pair with Elements class. Check the element by index from List[WebElement] is selected.
    returns bool element is selected
    """
    __slots__ = "_index"

    def __init__(self, owner: TypeElement, index: int) -> None:
        super().__init__(owner)
        self._index = index

    def __call__(self) -> bool:
        elements = self._owner.web_element if isinstance(self._owner.web_element, list) else [self._owner.web_element]
        self.debug_value = elements[self._index].is_selected()
        return self.debug_value


class WaitTextChangedAction(Action):
    """Waits until the text value from the element changes.
    self._owner.web_element is the WebElement
    value - is text value that will be change
    returns bool(WebElement.text != value)
    """
    __slots__ = "_value"

    def __init__(self, owner: TypeElement, value: str) -> None:
        super().__init__(owner)
        self._value = value

    def __call__(self) -> Union[bool, NoReturn]:
        self.debug_value = self._owner.web_element.text
        logging.debug(f"element.text: '{self.debug_value}'")
        if self.debug_value != self._value:
            return True
        else:
            raise NoSuchElementException


class GetSizeAction(Action):
    """Get self._element size x and y.
    self._owner.web_element is the WebElement
    returns dict
    """

    def __call__(self) -> Dict[str, int]:
        self.debug_value = self._owner.web_element.size
        return self.debug_value


class IsEnabledAction(Action):
    """Check is element enabled.
    self._owner.web_element is the WebElement
    returns bool
    """

    def __call__(self) -> bool:
        self.debug_value = self._owner.web_element.is_enabled()
        return self.debug_value

