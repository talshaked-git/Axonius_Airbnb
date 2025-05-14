from datetime import datetime
from playwright.sync_api import Page, expect
import logging


class HomePage:
    def __init__(self, page: Page):
        self.page = page

    def goto_home(self):
        self.page.goto("https://www.airbnb.com/homes", wait_until="load")

    def set_location(self, location: str):
        search_input = self.page.get_by_test_id("structured-search-input-field-query")
        search_input.click()
        logging.info(f"Typing {location} into search field")
        search_input.fill(location)

    def set_date(self, checkin: datetime, checkout: datetime):
        self.page.locator('div[role="button"]:has-text("Check in")').click()
        logging.info("Opening date selector")

        checkin_str = checkin.strftime('%Y-%m-%d')
        checkout_str = checkout.strftime('%Y-%m-%d')

        self.page.locator(f'button[data-state--date-string="{checkin_str}"]').first.click()
        logging.info(f"Clicked check-in date: {checkin_str}")

        self.page.locator(f'button[data-state--date-string="{checkout_str}"]').first.click()
        logging.info(f"Clicked check-out date: {checkout_str}")

    def set_guests(self, adults: int = 1, children: int = 0, infants: int = 0, pets: int = 0):
        self.page.get_by_role("button", name="Who Add guests").click()

        logging.info("Setting guests")
        for _ in range(adults):
            self.page.get_by_test_id("stepper-adults-increase-button").first.click()
        for _ in range(children):
            self.page.get_by_test_id("stepper-children-increase-button").first.click()
        for _ in range(infants):
            self.page.get_by_test_id("stepper-infants-increase-button").first.click()
        for _ in range(pets):
            self.page.get_by_test_id("stepper-pets-increase-button").first.click()

    def submit_search(self):
        logging.info("Clicking on submit search")
        self.page.get_by_test_id("structured-search-input-search-button").click()

    def search_bnb(self, location: str, checkin: datetime, checkout: datetime,
                   adults: int = 1, children: int = 0, infants: int = 0, pets: int = 0):
        self.goto_home()
        self.disable_auto_translation()
        self.set_location(location)
        self.set_date(checkin, checkout)
        self.set_guests(adults, children, infants, pets)
        self.submit_search()

    def disable_auto_translation(self):
        self.page.get_by_role("button", name="Choose a language and currency").click()
        self.page.locator('button[role="switch"][aria-labelledby="auto_translate_switch"]').click()
        self.page.locator('[role="dialog"][aria-label="Languages"]').wait_for(state='hidden', timeout=5000)
        logging.info("Disabled auto translation feature to avoid reservation pop-up")

    def format_dates_for_validate(self, checkin: datetime, checkout: datetime):
        try:
            if checkin.month == checkout.month:
                return f"{checkin.strftime('%B %-d')} – {checkout.strftime('%-d')}"
            else:
                return f"{checkin.strftime('%B %-d')} – {checkout.strftime('%B %-d')}"
        except ValueError:
            if checkin.month == checkout.month:
                day1 = checkin.strftime('%d').lstrip('0')
                day2 = checkout.strftime('%d').lstrip('0')
                return f"{checkin.strftime('%B')} {day1} – {day2}"
            else:
                day1 = checkin.strftime('%d').lstrip('0')
                day2 = checkout.strftime('%d').lstrip('0')
                return f"{checkin.strftime('%B')} {day1} – {checkout.strftime('%B')} {day2}"

    def validate_little_search(self, location, checkin, checkout, guests):
        location_locator = self.page.get_by_test_id("little-search-location")
        dates_locator = self.page.get_by_test_id("little-search-anytime")
        guests_locator = self.page.get_by_test_id("little-search-guests")

        expect(location_locator).to_contain_text(location)

        duration = self.format_dates_for_validate(checkin, checkout)
        expect(dates_locator).to_contain_text(duration)

        expect(guests_locator).to_contain_text(guests)
