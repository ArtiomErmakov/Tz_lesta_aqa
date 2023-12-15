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

