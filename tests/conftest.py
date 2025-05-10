import pytest
from playwright.sync_api import Page
from src.page_objects.home_page import HomePage
from src.page_objects.reservation_page import ReservationPage
from src.page_objects.results_page import ResultsPage


class PageManager:
    def __init__(self, page: Page):
        self.page = page
        self.home_page = HomePage(page)
        self.results_page = ResultsPage(page)
        self.reservation_page = ReservationPage(page)


@pytest.fixture
def pages(page: Page):
    return PageManager(page)
