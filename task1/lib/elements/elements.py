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
