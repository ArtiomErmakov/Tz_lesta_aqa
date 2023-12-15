from dataclasses import dataclass

from .locator import Locator
from ..by_type import ByType
from ..constants import Url


@dataclass
class ProgrammingLanguagesLocators:
    PROGRAMMING_LANGUAGES_URL = Locator(f"{Url.SRV_URL}", by=ByType.URL)
    PROGRAMMING_LANGUAGES_SANITY_ELEMENT = Locator("//table/caption[contains(text(),'Programming languages')]")
    ALL_WEBSITES_ELEMENTS = Locator("//table[1]//tbody//tr")
    WEBSITE_NAME_BY_ROW_TABLE_CELL = Locator("//table[1]//tbody//tr[{}]/td[1]/a")
    POPULARITY_BY_ROW_TABLE_CELL = Locator("//table[1]//tbody//tr[{}]/td[2]")
    FRONT_END_BY_ROW_TABLE_CELL = Locator("//table[1]//tbody//tr[{}]/td[3]")
    BACK_END_BY_ROW_TABLE_CELL = Locator("//table[1]//tbody//tr[{}]/td[4]")
    DATABASE_BY_ROW_TABLE_CELL = Locator("//table[1]//tbody//tr[{}]/td[5]")
    NODE_BY_ROW_TABLE_CELL = Locator("//table[1]//tbody//tr[{}]/td[6]")
