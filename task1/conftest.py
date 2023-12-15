import pytest
from selenium import webdriver
from typing import Any, Generator


@pytest.fixture(scope="session", autouse=True)
def driver() -> Generator[webdriver.Chrome, Any, None]:
    driver = webdriver.Chrome()
    yield driver
    driver.quit()
