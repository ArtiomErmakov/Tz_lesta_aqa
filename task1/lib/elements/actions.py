import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Union, NoReturn, Dict, Any, TypeVar, Callable

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
