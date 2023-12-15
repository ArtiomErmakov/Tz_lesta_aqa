import logging
import time
from typing import Optional, NoReturn

from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver

from ..constants import Const, Times


class Page:
    """Base class for page object model."""

    def __init__(self, driver: WebDriver) -> None:
        self._driver = driver
        url = self._URL
        logging.info(f"Calling griver.get('{url}')...")
        self._driver.get(url)
        logging.info("Finished calling driver.get()...")
        self._post_init()

    def _post_init(self):
        self.sanity_check()
        logging.info("Sleeping 3 sec...")
        time.sleep(Times.THREE_SECONDS)    # delay that eliminates errors after page loading

    def sanity_check(self, check_url: bool = True, check_title: bool = False) -> Optional[NoReturn]:
        """Simplest test that checks is selenium working, and is web page loading."""

        # It will wait until expected condition happen (for example element is loaded and located)
        logging.info("Initializing WebDriverWait...")
        wait = WebDriverWait(driver=self._driver,
                             timeout=Const.ELEMENT_WAIT_TIMEOUT,
                             poll_frequency=Const.POLL_FREQUENCY)
        if check_url:
            logging.info(f"Starting sanity check url '{self._URL}'...")
            # self._driver.save_screenshot(f"sanity_url_{time.time()}.png")
            # is current_url self._URL?
            url_to_be_condition = expected_conditions.url_to_be(self._URL)
            assert wait.until(url_to_be_condition, message=f'Error, Sanity check URL={self._URL} failed!')
            logging.info("Finished sanity check url...")

        if check_title:
            logging.info(f"Starting sanity check page title '{self._PAGE_TITLE}'...")
            # self._driver.save_screenshot(f"sanity_title_{time.time()}.png")
            # is page title LOGIN_PAGE_TITLE?
            title_match_condition = expected_conditions.title_is(self._PAGE_TITLE)
            assert wait.until(title_match_condition)
            logging.info("Finished sanity check page title...")

    @property
    def driver(self) -> WebDriver:
        return self._driver

    @property
    def title(self) -> str:
        return self._driver.title

    def refresh(self):
        self._driver.refresh()
        time.sleep(Times.THREE_SECONDS)
