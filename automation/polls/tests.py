# from django.test import TestCase

# Create your tests here.
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Dict, List
from unittest import TestCase

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class SeleniumTest(TestCase):

    # batman token - 4f63268adbfa2f5ec361a3033f8011c3d461721f
    def test_selenium(self):
        driver: ImdbSeleniumDriver = ImdbSeleniumDriver(custom_driver_path='/Users/idan.aviv/Downloads/chromedriver_v98_0')
        print(driver.query_movies('location', 'America', 200))


@dataclass
class SearchMovieResult:

    title: str
    year: str
    score: float


class BrowserType(Enum):
    CHROME = 'chrome'
    FIREFOX = 'firefox'


class ImdbSeleniumDriver:

    _IMDB_BASE_URL: str = "https://www.imdb.com/search/"
    _LOCATORS_MAP: Dict[str, str] = {"search_type": "//option[@value='${}']",
                                     "search_box": "query",
                                     "submit_bth": "//form[@action='/search/title-text/']//button[@type='submit']",
                                     "search_results_container": "lister-list",
                                     "result_item_container": ".//div[@class='lister-item mode-detail']",
                                     "title": ".//h3/a",
                                     "year": ".//span[@class='lister-item-year text-muted unbold']",
                                     "next_bth": "//a[@class='lister-page-next next-page']"}

    def __init__(self, browser_type: BrowserType = BrowserType.CHROME, custom_driver_path: str = '/usr/local/bin') -> None:
        super().__init__()
        self.driver: WebDriver = self._create_driver(browser_type, custom_driver_path)

    @staticmethod
    def _create_driver(browser_type: BrowserType, custom_driver_path: str) -> WebDriver:
        driver: WebDriver
        if browser_type == BrowserType.CHROME:
            driver = webdriver.Chrome(executable_path=custom_driver_path)
        elif browser_type == BrowserType.FIREFOX:
            driver = webdriver.Firefox(executable_path=custom_driver_path)  # init FF driver here
        else:
            raise Exception('invalid browser type')
        driver.maximize_window()
        return driver

    def query_movies(self, search_type: str, query: str, limit: int) -> dict:
        results: List[SearchMovieResult] = self._query_movies(search_type, query, limit)
        return self._movie_results_to_json(results)

    def _query_movies(self, search_type: str, query: str, limit: int) -> List[SearchMovieResult]:
        # self.driver.implicitly_wait(5)
        self.driver.get(self._IMDB_BASE_URL)
        select_category_elm: WebElement = self.driver.find_element(By.XPATH, self._create_locator('search_type', search_type))
        select_category_elm.click()

        search_box_elm: WebElement = self.driver.find_element(By.ID, self._create_locator('search_box'))
        search_box_elm.send_keys(query)

        search_bth_elm: WebElement = self.driver.find_element(By.XPATH, self._create_locator('submit_bth'))
        search_bth_elm.click()
        search_results: List[SearchMovieResult] = []
        self._load_search_results(search_results, limit)
        return search_results

    @staticmethod
    def _movie_results_to_json(search_results: List[SearchMovieResult]) -> dict:
        results: list = [asdict(res) for res in search_results]
        return {'search_results': results, 'size': len(results)}

    def _load_search_results(self, search_results: List[SearchMovieResult], limit: int):
        while len(search_results) < limit:
            if self._load_single_page_search_results(search_results, limit) or not self._click_next():
                break

    def _click_next(self) -> bool:
        try:
            next_bth: WebElement = self.driver.find_element(By.XPATH, self._create_locator('next_bth'))
            if next_bth.is_displayed() and next_bth.is_enabled():
                next_bth.click()
                return True
        except Exception:
            pass
        return False

    def _load_single_page_search_results(self, search_results: List[SearchMovieResult], limit: int) -> bool:
        for res_elm in self.driver.find_element(By.CLASS_NAME, self._create_locator('search_results_container'))\
                .find_elements(By.XPATH, self._create_locator('result_item_container')):
            res: SearchMovieResult = SearchMovieResult(title=res_elm.find_element(By.XPATH, self._create_locator('title')).text,
                                                       year=res_elm.find_element(By.XPATH, self._create_locator('year'))
                                                       .text.replace('(', '').replace(')', ''),
                                                       score=8.0)  # todo - float(res_elm.find_element(By.XPATH, ".//strong").text)
            search_results.append(res)
            if len(search_results) == limit:
                return True
        return False

    @classmethod
    def _create_locator(cls, locator_name: str, param_value: str = None) -> str:
        locator: str = cls._LOCATORS_MAP.get(locator_name)
        return f'{locator.replace("${}", param_value)}' if param_value else locator

    def quit(self):
        self.driver.quit()
