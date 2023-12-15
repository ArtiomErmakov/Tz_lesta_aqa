import re
from selenium.common.exceptions import TimeoutException
import logging
from typing import Optional, NoReturn, List
from .page import Page
from ..elements.elements import Element, Elements, TableCell
from ..locators.locators_programming_language import ProgrammingLanguagesLocators
from ..constants import Times

PROGRAMMING_LANGUAGE_PAGE_TITLE = "Programming languages used in most popular websites"


class ProgrammingLanguagePage(Page):
    _PAGE_TITLE = PROGRAMMING_LANGUAGE_PAGE_TITLE
    _locs: ProgrammingLanguagesLocators
    _sanity: Element

    _all_website_elements: Elements
    _website_name_by_row_table_cell: TableCell
    _popularity_by_row_table_cell: TableCell
    _front_end_by_row_table_cell: TableCell
    _back_end_by_row_table_cell: TableCell
    _database_by_row_table_cell: TableCell
    _note_by_row_table_cell: TableCell

    def __init__(self, driver) -> None:
        logging.info("Initializing ProgrammingLanguagesLocators...")
        ProgrammingLanguagePage._locs = ProgrammingLanguagesLocators()
        _, self._URL = self._locs.PROGRAMMING_LANGUAGES_URL
        super().__init__(driver)
        self.sanity_check()
        self._post_init()

    def sanity_check(self, check_url: bool = True, check_title: bool = True) -> Optional[NoReturn]:
        super().sanity_check()
        ProgrammingLanguagePage._sanity = Element(self._locs.PROGRAMMING_LANGUAGES_SANITY_ELEMENT)
        logging.info("Start waiting sanity element on programming languages  page...")
        self._sanity.wait_on_page()
        logging.info("Finished waiting sanity element on programming languages page...")

    @classmethod
    def _post_init(cls):
        pass

    def get_count_all_websites(self) -> int:
        try:
            ProgrammingLanguagePage._all_website_elements = Elements(self._locs.ALL_WEBSITES_ELEMENTS,
                                                                     timeout=Times.TEN_SECONDS)
            return self._all_website_elements.length
        except TimeoutException:
            return 0

    def get_website_name_by_row_table_cell(self, row: int) -> str:
        ProgrammingLanguagePage._website_name_by_row_table_cell = TableCell(self._locs.WEBSITE_NAME_BY_ROW_TABLE_CELL(
            row))
        return self._website_name_by_row_table_cell.text

    def get_popularity_by_row_table_cell(self, row: int) -> float:
        ProgrammingLanguagePage._popularity_by_row_table_cell = TableCell(self._locs.POPULARITY_BY_ROW_TABLE_CELL(row))
        popularity = self._popularity_by_row_table_cell.text.split('[')[0]
        numbers = re.findall(r'\b\d+\b', popularity)
        return float(''.join(numbers))

    def get_front_end_by_row_table_cell(self, row: int) -> List[str]:
        ProgrammingLanguagePage._front_end_by_row_table_cell = TableCell(self._locs.FRONT_END_BY_ROW_TABLE_CELL(row))
        return self._front_end_by_row_table_cell.text.split(',')

    def get_back_end_by_row_table_cell(self, row: int) -> List[str]:
        ProgrammingLanguagePage._back_end_by_row_table_cell = TableCell(self._locs.BACK_END_BY_ROW_TABLE_CELL(row))
        return self._back_end_by_row_table_cell.text.split(',')

    def get_database_by_row_table_cell(self, row: int) -> List[str]:
        ProgrammingLanguagePage._database_by_row_table_cell = TableCell(self._locs.DATABASE_BY_ROW_TABLE_CELL(row))
        return self._database_by_row_table_cell.text.split(',')

    def get_note_by_row_table_cell(self, row: int) -> Optional[str]:
        ProgrammingLanguagePage._note_by_row_table_cell = TableCell(self._locs.NODE_BY_ROW_TABLE_CELL(row))
        return self._note_by_row_table_cell.text
