import pytest
from selenium import webdriver
from typing import Any, Generator
from selenium.webdriver.remote.webdriver import WebDriver


@pytest.fixture(scope="session", autouse=True)
def driver() -> Generator[WebDriver, Any, None]:
    driver = webdriver.Chrome()
    yield driver
    driver.quit()
