from abc import ABC
import logging

from typing import List, Optional
from dataclasses import dataclass
from ..pages.page_programming_languages import ProgrammingLanguagePage
from selenium.webdriver.remote.webdriver import WebDriver


@dataclass
class ProgrammingLanguages:
    website: Optional[str] = None
    popularity: float = 0.0
    front_end: Optional[List[str]] = None
    back_end: Optional[List[str]] = None
    database: Optional[List[str]] = None
    note: Optional[str] = None

