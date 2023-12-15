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


class ProgrammingLanguagesUI(ABC):

    @staticmethod
    def _get_programming_languages_used_in_most_popular_websites(driver: WebDriver) -> List[ProgrammingLanguages]:
        logging.info(f"Run _get_programming_languages_used_in_most_popular_websites()")
        programming_languages_page = ProgrammingLanguagePage(driver=driver)

        num_website = programming_languages_page.get_count_all_websites()
        websites_list = []
        for row in range(1, num_website + 1):
            website = programming_languages_page.get_website_name_by_row_table_cell(row)
            popularity = programming_languages_page.get_popularity_by_row_table_cell(row)
            front_end = programming_languages_page.get_front_end_by_row_table_cell(row)
            back_end = programming_languages_page.get_back_end_by_row_table_cell(row)
            database = programming_languages_page.get_database_by_row_table_cell(row)
            note = programming_languages_page.get_note_by_row_table_cell(row)
            websites_list.append(ProgrammingLanguages(website, popularity, front_end, back_end, database, note))
        return websites_list
