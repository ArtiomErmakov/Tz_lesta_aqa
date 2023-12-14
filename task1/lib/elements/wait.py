import datetime
import logging
import time

from typing import Callable, Optional, Tuple, Union, List

from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from ..constants import Const
from .actions import TypeElement


IGNORED_EXCEPTIONS = (NoSuchElementException,
                      ElementClickInterceptedException,
                      ElementNotInteractableException,
                      StaleElementReferenceException)


class WebDriverWaitTill(WebDriverWait):
    """Class extends selenium WebDriverWait."""
    __slots__ = "_date"

    def __init__(self,
                 driver: WebDriver,
                 timeout: int,
                 poll_frequency: float = Const.POLL_FREQUENCY,
                 ignored_exceptions: Optional[Tuple[Exception]] = None,
                 date: Optional[datetime.datetime] = None) -> None:
        super().__init__(driver, timeout, poll_frequency=poll_frequency, ignored_exceptions=ignored_exceptions)
        self._date: Optional[datetime.datetime] = date

    def till(self, method: Callable[[Union[Tuple[str, str], List[Tuple[str, str]]]],
                                    Union[TypeElement, List[TypeElement]]]) -> bool:
        """Calls the method provided with the driver as an argument until the
        return value is not True. If method's value is True - returns False.
        When timeout expired return True."""

        end_time = time.time() + self._timeout
        while True:
            try:
                value = method(self._driver)
                if value:
                    return False
            except self._ignored_exceptions:
                pass
            time.sleep(self._poll)
            if time.time() > end_time:
                break
        return True

    def till_date(self, method: Callable[[Union[Tuple[str, str], List[Tuple[str, str]]]],
                                         Union[TypeElement, List[TypeElement]]]) -> bool:
        """Calls the method provided with the driver as an argument until the
        return value is True. If success is not True - returns False.
        When current datetime exceeded date - returns True."""

        date_str = self._date.strftime('%Y-%m-%d %H:%M:%S')
        logging.info(f"Waiting till '{date_str}'")

        while True:
            try:
                success = method(self._driver)
            except self._ignored_exceptions:
                success = False

            if datetime.datetime.now() >= self._date:
                return True

            if not success:
                return False
            time.sleep(self._poll)
