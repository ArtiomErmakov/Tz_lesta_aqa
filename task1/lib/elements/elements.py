import datetime
import logging
import time
from typing import Tuple, Union, NoReturn, Optional, Any, List, Dict, TypeVar, Callable

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.remote.webelement import WebElement


from .actions import ClearAction, ClickAction, ReadTextAction, SendKeysAction, IsOnPageAction, GetLenAction, Action
from .actions import IsEnabledAction, ClickByIndexElementsAction, IsSelectedByIndexElementsAction, SubmitAction
from .actions import WaitTextAction, IsSelectedAction, ReadTextListAction, GetAttributeAction, GetPropertyAction
from .actions import WaitTextChangedAction, GetSizeAction, ReadPropertyListAction, ReadAttributeListAction
from .actions import IncompleteListActionError, TypeElement
from .wait import IGNORED_EXCEPTIONS
from .wait import WebDriverWaitTill
from ..constants import Const, Times
from ..locators.locator import Locator

TypeAction = TypeVar('TypeAction', bound=Action)  # any subclass of Action
TypePage = TypeVar('TypePage', bound='Page')  # any subclass of Page

FIND_ELEMENT_INTERNAL_TIMEOUT = Times.TWO_SECONDS


class Element:
    """Base class for web page elements."""

    __slots__ = ("_locator", "web_element", "_condition", "_timeout", "_web_driver", "_date")

    # condition for WebDriverWait
    _default_condition = expected_conditions.presence_of_element_located

    def __init__(self, locator: Union[Tuple[str, str], List[Tuple[str, str]]],
                 timeout: int = Const.ELEMENT_WAIT_TIMEOUT,
                 date: Optional[datetime.datetime] = None
                 ) -> None:

        self._locator: Union[Tuple[str, str], List[Tuple[str, str]]] = locator
        self.web_element: Optional[WebElement] = None
        self._condition: Callable[[Union[Tuple[str, str], List[Tuple[str, str]]]],
                                  Union[TypeElement, List[TypeElement]]] = self._init_condition(self._locator)
        self._timeout: int = timeout
        self._web_driver: Optional[WebDriver] = None
        self._date: Optional[datetime.datetime] = date

    @classmethod
    def _init_condition(cls, locator: Union[Tuple[str, str], List[Tuple[str, str]]]
                        ) -> Callable[[Union[Tuple[str, str], List[Tuple[str, str]]]],
                                      Union[TypeElement, List[TypeElement]]]:
        if isinstance(locator, Locator) or (isinstance(locator, list) and locator and isinstance(locator[0], Locator)):
            raise TypeError(f"Expected locator=tuple(by, locator) or List[tuple], but  actually {locator=}."
                            f" Possibly locator uses formatted string literals {{}} or {{kwarg}}."
                            f" Check your Page class, usage example LOCATOR_ELEMENT(arg1, arg2,..., kwarg3=kwarg3,...)")

        return cls._default_condition(locator)

    def __get__(self, instance: TypePage, owner: Optional[TypePage] = None) -> TypeElement:
        """When we try to read data from class object, returns wrapped
         web element."""
        self._web_driver = instance.driver

        end_time = time.time() + self._timeout
        while True:
            try:
                self._find_element()
                break
            except (*IGNORED_EXCEPTIONS, TimeoutException):
                if time.time() > end_time:
                    raise
            time.sleep(Const.POLL_FREQUENCY)

        return self

    def _find_element(self) -> Optional[NoReturn]:
        # wait until expected condition (for example element is loaded and located)
        wait = WebDriverWaitTill(driver=self._web_driver,
                                 timeout=FIND_ELEMENT_INTERNAL_TIMEOUT,
                                 poll_frequency=Const.POLL_FREQUENCY,
                                 ignored_exceptions=IGNORED_EXCEPTIONS,
                                 date=self._date)

        try:
            self.web_element = wait.until(self._condition)
        except TimeoutException:
            err_message = (f"No such element: {self.__class__.__name__}, locator={self._locator},"
                           f" condition={self._condition}, timeout={self._timeout}")
            raise TimeoutException(err_message)

    def _safe_interact(self,
                       action: TypeAction,
                       message: str = '') -> Union[Any, NoReturn]:
        """Try rerun action() again and again, while it will be done,
        because DOM could change suddenly, and the result may be reached far from
        the first attempt."""

        end_time = time.time() + self._timeout
        while True:
            try:
                self._find_element()
                return action()
            except (*IGNORED_EXCEPTIONS, TimeoutException):
                pass
            time.sleep(Const.POLL_FREQUENCY)
            if time.time() > end_time:
                break
        message_text = ""
        if message:
            message_text = (f"Timeout expired, '{self.__class__.__name__}', locator={self._locator}, {self.web_element}"
                            f", {message} {action.debug_value}.")
            logging.info(message_text)
        raise TimeoutException(message_text)

    def _click(self) -> Optional[NoReturn]:
        message = "can't click"
        self._safe_interact(ClickAction(self), message=message)

    def _clear(self) -> Optional[NoReturn]:
        message = "can't clear"
        self._safe_interact(ClearAction(self), message=message)

    def _get_text(self) -> Union[str, NoReturn]:
        message = "can't read text"
        return self._safe_interact(ReadTextAction(self), message=message)

    def _send_keys(self, value: Optional[str]) -> Optional[NoReturn]:
        message = f"can't send keys '{value}'"
        if value is not None:
            self._safe_interact(SendKeysAction(self, value), message=message)

    def _get_len(self) -> Union[int, NoReturn]:
        return self._safe_interact(GetLenAction(self))

    def _wait_text(self, value: Optional[str]) -> Union[bool, NoReturn]:
        message = f"expected text '{value}' != "
        action = WaitTextAction(self, value)
        return self._safe_interact(action, message=message)

    def _wait_text_bool_result(self, value: Optional[str]) -> bool:
        try:
            return self._wait_text(value)
        except TimeoutException:
            return False

    def _is_selected(self) -> bool:
        return self._safe_interact(IsSelectedAction(self))

    def _get_attribute(self, attr_name: str) -> Optional[str]:
        return self._safe_interact(GetAttributeAction(self, attr_name))

    def _get_property(self, prop_name: str) -> Optional[str]:
        """Reads DOM property, that value is not visible in the html markup"""
        return self._safe_interact(GetPropertyAction(self, prop_name))

    def _click_by_index_elements(self, index: int) -> Optional[NoReturn]:
        message = "can't click"
        self._safe_interact(ClickByIndexElementsAction(self, index), message=message)

    def _is_selected_by_index_elements(self, index: int) -> bool:
        return self._safe_interact(IsSelectedByIndexElementsAction(self, index))

    def _wait_until_text_changed(self, value: str = '') -> Union[bool, NoReturn]:
        message = f"'{value}' text not changed"
        action = WaitTextChangedAction(self, value)
        return self._safe_interact(action, message=message)

    def _wait_until_text_changed_bool_result(self) -> bool:
        try:
            return self._wait_until_text_changed()
        except TimeoutException:
            return False

    def _drag_and_drop_by_offset(self, xoffset: int, yoffset: int) -> Optional[NoReturn]:
        actions = ActionChains(self._web_driver)
        actions.drag_and_drop_by_offset(self.web_element, xoffset, yoffset)
        actions.perform()

    def _get_size(self) -> Union[Dict[str, int], NoReturn]:
        return self._safe_interact(GetSizeAction(self))

    def _right_click(self) -> Optional[NoReturn]:
        actions = ActionChains(self._web_driver)
        actions.context_click(self.web_element).perform()

    def _is_enabled(self) -> bool:
        return self._safe_interact(IsEnabledAction(self))

    def _submit(self) -> Optional[NoReturn]:
        self._safe_interact(SubmitAction(self))

    ####################################################################################################################
    # public methods
    def is_on_page(self) -> Union[bool, NoReturn]:
        return self._safe_interact(IsOnPageAction(self))

    def wait_on_page(self) -> Optional[NoReturn]:
        self._find_element()

    def scroll_down(self) -> None:
        self._send_keys(Keys.PAGE_DOWN)

    def get_attribute(self, attr_name) -> Optional[str]:
        return self._get_attribute(attr_name)


class Button(Element):

    def __init__(self, locator: Tuple[str, str], timeout: int = Const.ELEMENT_WAIT_TIMEOUT) -> None:
        super().__init__(locator, timeout=timeout)
        self._condition: Callable[[Tuple[str, str]],
                                  TypeElement] = expected_conditions.element_to_be_clickable(self._locator)

    @property
    def text(self) -> str:
        return self._get_text()

    def click(self) -> None:
        self._click()

    def get_attribute(self, attr_name: str) -> Optional[str]:
        return self._get_attribute(attr_name)

    def get_property(self, name: str) -> str:
        return self._get_property(name)


class Input(Element):
    """Class for checking status of checkbox (is_selected() method). Input is NOT CLICKABLE!!! , for example:
        <div>
            <input id="something_id" type="checkbox"> - use this element we can check status of the checkbox
            <label for="something_id">Checkbox text</label> - we can click by this element
        </div>
    """

    def is_selected(self) -> bool:
        return self._is_selected()

    def clear(self) -> None:
        self._clear()

    def send_keys(self, value: Optional[str]) -> None:
        self._send_keys(value)

    def get_property(self, name: str) -> str:
        return self._get_property(name)

    def set_focus(self) -> None:
        self._send_keys("")

    def click(self) -> None:
        self._click()

    def press_enter(self) -> None:
        self._submit()


class Checkbox(Element):
    """Class for checkboxes or radio buttons. It's really work in pair with <label> element, for example:
        <div>
            <input id="something_id" type="checkbox"> - we check status only
            <label for="something_id">Checkbox text</label> - we can click, and read text only
        </div>
    """

    def __init__(self, locator: Tuple[str, str], timeout: int = Const.ELEMENT_WAIT_TIMEOUT) -> None:
        super().__init__(locator, timeout=timeout)
        self._condition: Callable[[Tuple[str, str]],
                                  TypeElement] = expected_conditions.element_to_be_clickable(self._locator)

    @property
    def text(self) -> str:
        return self._get_text()

    def click(self) -> None:
        self._click()


class Field(Element):
    """Text Field element class. Can to: get text, clear, click, send keys."""

    @property
    def text(self) -> str:
        return self._get_text()

    def clear(self) -> None:
        self._clear()

    def click(self) -> None:
        self._click()

    def wait_text(self, value: Optional[str] = None) -> bool:
        return self._wait_text_bool_result(value)

    def send_keys(self, value: Optional[str]) -> None:
        self._send_keys(value)

    def wait_until_text_changed(self) -> bool:
        return self._wait_until_text_changed_bool_result()

    def get_property(self, name: str) -> str:
        return self._get_property(name)

    def right_click(self) -> None:
        self._right_click()

    def is_enabled(self) -> bool:
        return self._is_enabled()

    def press_enter(self) -> None:
        self._submit()


class ClickableField(Field):
    def __init__(self, locator: Tuple[str, str], timeout: int = Const.ELEMENT_WAIT_TIMEOUT) -> None:
        super().__init__(locator, timeout=timeout)
        self._condition: Callable[[Tuple[str, str]],
                                  TypeElement] = expected_conditions.element_to_be_clickable(self._locator)


class NoElementPresent(Element):
    """Class for element that shouldn't be on page. If the element appears -
    something is going wrong."""

    def __get__(self, instance: TypePage, owner: Optional[TypePage] = None) -> bool:
        web_driver = instance.driver  # type: WebDriver

        wait = WebDriverWaitTill(driver=web_driver,
                                 timeout=self._timeout,
                                 poll_frequency=Const.POLL_FREQUENCY,
                                 ignored_exceptions=IGNORED_EXCEPTIONS)

        return wait.till(self._condition)


class Link(Element):
    """Class for Hyperlinks"""

    def __init__(self, locator: Tuple[str, str], timeout: int = Const.ELEMENT_WAIT_TIMEOUT) -> None:
        super().__init__(locator, timeout=timeout)
        self._condition: Callable[[Tuple[str, str]],
                                  TypeElement] = expected_conditions.element_to_be_clickable(self._locator)

    def click(self) -> None:
        self._click()

    def wait_text(self, value: Optional[str] = None) -> bool:
        return self._wait_text_bool_result(value)

    @property
    def text(self) -> str:
        return self._get_text()


class Elements(Element):
    """Class works with a group of elements selected by one locator"""

    __slots__ = ("incomplete_result", "start_index")
    _default_condition = expected_conditions.presence_of_all_elements_located

    def __init__(self, locator: Union[Tuple[str, str], List[Tuple[str, str]]],
                 timeout: int = Const.ELEMENT_WAIT_TIMEOUT,
                 date: Optional[datetime.datetime] = None
                 ) -> None:
        super().__init__(locator, timeout, date)
        self.incomplete_result: List[str] = []
        self.start_index: int = 0

    def _safe_list_interact(self,
                            action: TypeAction,
                            message: str = '') -> Union[Any, NoReturn]:
        """Try rerun action() again and again, while it will be done,
        because DOM could change suddenly, and the result may be reached far from
        the first attempt."""

        # reinit vars for processing result before starting interaction
        self.start_index = 0
        self.incomplete_result = []

        end_time = time.time() + self._timeout
        while True:
            try:
                self._find_element()
                return action()
            except (*IGNORED_EXCEPTIONS, TimeoutException, IncompleteListActionError):
                pass

            time.sleep(Const.POLL_FREQUENCY)
            if time.time() > end_time:
                break
        message_text = ""
        if message:
            message_text = (f"Timeout expired, '{self.__class__.__name__}', locator={self._locator}, {self.web_element}"
                            f", {message} {action.debug_value}.")
            logging.info(message_text)
        raise TimeoutException(message_text)

    def _get_text_list(self) -> Union[List[str], NoReturn]:
        message = "can't read text list"
        return self._safe_list_interact(ReadTextListAction(self), message=message)

    def _get_property_list(self, prop_name: str) -> Union[List[str], NoReturn]:
        message = f"can't read prop '{prop_name}' list"
        return self._safe_list_interact(ReadPropertyListAction(self, prop_name), message=message)

    def _get_attribute_list(self, attr_name: str) -> Union[List[str], NoReturn]:
        message = f"can't read attr '{attr_name}' list"
        return self._safe_list_interact(ReadAttributeListAction(self, attr_name), message=message)

    @property
    def length(self) -> int:
        return self._get_len()

    @property
    def text_list(self) -> List[str]:
        return self._get_text_list()

    def get_property_list(self, prop_name: str) -> List[str]:
        return self._get_property_list(prop_name)

    def get_attribute_list(self, attr_name: str) -> List[str]:
        return self._get_attribute_list(attr_name)

    def click_by_index(self, index: int) -> None:
        self._click_by_index_elements(index)

    def is_selected_by_index(self, index: int) -> bool:
        return self._is_selected_by_index_elements(index)


class TableCell(Element):

    @property
    def text(self) -> str:
        return self._get_text()

    def get_attribute(self, attr_name: str) -> Optional[str]:
        return self._get_attribute(attr_name)

    def click(self) -> None:
        self._click()


class ElementPresentTillDate(Element):
    """Class for element that should be on page. If the element disappears -
    returns False."""

    def __get__(self, instance: TypePage, owner: Optional[TypePage] = None) -> bool:
        web_driver = instance.driver  # type: WebDriver

        wait = WebDriverWaitTill(driver=web_driver,
                                 timeout=self._timeout,
                                 poll_frequency=Const.POLL_FREQUENCY,
                                 ignored_exceptions=IGNORED_EXCEPTIONS,
                                 date=self._date)

        return wait.till_date(self._condition)


class MenuItem(Element):

    def __init__(self, locator: Tuple[str, str], timeout: int = Const.ELEMENT_WAIT_TIMEOUT) -> None:
        super().__init__(locator, timeout=timeout)
        self._condition: Callable[[Tuple[str, str]],
                                  TypeElement] = expected_conditions.element_to_be_clickable(self._locator)

    def click(self) -> None:
        self._click()

    @property
    def text(self) -> str:
        return self._get_text()


class Slider(Element):

    def set_percent(self, percent: int) -> None:
        height = self._get_size()['height']
        width = self._get_size()['width']

        if width > height:
            # highly likely a horizontal slider
            self._drag_and_drop_by_offset(int(width / 100 * (percent - 50)), 0)
        else:
            # highly likely a vertical slider
            self._drag_and_drop_by_offset(0, int(height / 100 * (percent - 50)))


class ElementThatWillDisappear(Element):
    """Class for element that presents on page, and later that element should
     disappear during the timeout.
     """

    def __get__(self, instance: TypePage, owner: Optional[TypePage] = None) -> bool:
        web_driver = instance.driver  # type: WebDriver

        wait = WebDriverWaitTill(driver=web_driver,
                                 timeout=self._timeout,
                                 poll_frequency=Const.POLL_FREQUENCY,
                                 ignored_exceptions=IGNORED_EXCEPTIONS)

        return wait.until_not(self._condition)


class IndexOneOfElementsLocated:
    """ Custom Expected Condition

     An expectation for checking that there is at least one element presents
    on a web page.
    locator is used to find the element - it is List[locator] = List[Tuple[str, str]]
    returns - index of found element in the locators list
    """
    __slots__ = "locator"

    def __init__(self, locator: List[Tuple[str, str]]) -> None:
        self.locator = locator

    def __call__(self, driver: WebDriver) -> Union[str, NoReturn]:
        for num, locator in enumerate(self.locator):
            result = None
            try:
                result = driver.find_element(*locator)
                time.sleep(Const.POLL_FREQUENCY)
            except (NoSuchElementException, WebDriverException):
                pass
            if result:
                return str(num)
        raise NoSuchElementException(f"No such element: {self.locator}")
