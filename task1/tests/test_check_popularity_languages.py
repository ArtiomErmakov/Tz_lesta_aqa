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

    @pytest.mark.parametrize(
        "parameter_count",
        [
            pytest.param(10**7),
            pytest.param(1.5 * 10**7),
            pytest.param(5 * 10**7),
            pytest.param(10**8),
            pytest.param(5 * 10**8),
            pytest.param(10**9),
            pytest.param(1.5 * 10**9)
        ]
    )
    def test_check_popularity_languages(self, driver: WebDriver,
                                        parameter_count: float):
        websites: List[ProgrammingLanguages] = ProgrammingLanguagesUI(
            )._get_programming_languages_used_in_most_popular_websites(driver)
        failures: List[str] = []
        for website in websites:
            self._check_popularity_on_website(website, failures, parameter_count)
        if failures:
            utils.raise_assert(failures)
