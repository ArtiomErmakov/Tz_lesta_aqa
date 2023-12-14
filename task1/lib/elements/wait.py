import datetime
import logging
import time

from typing import Callable, Optional, Tuple, Union, List, TypeVar

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


