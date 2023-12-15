import pytest

from selenium.webdriver.remote.webdriver import WebDriver
from ..lib.server_ui.programming_languages_ui import ProgrammingLanguages, ProgrammingLanguagesUI
from ..lib import utils
from typing import List


class TestCheckPopularityLanguages:
    @staticmethod
    def _check_popularity_on_website(website: ProgrammingLanguages,
                                     failures: List[str],
                                     count: float) -> None:
        if website.popularity < count:
            failures.append(f"{website.website} (Frontend:{website.front_end}|Backend{website.back_end}) "
                            f"has {website.popularity} unique visitor per month. Expected more {count}  ")

