import pytest
from selenium import webdriver


@pytest.fixture(scope="session", autouse=True)
def driver():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()
