import logging
from playwright.sync_api import Page, expect


class ReservationPage:
    def __init__(self, page: Page):
        self.page = page

    def parse_and_validate_summary(self):
        self.page.wait_for_timeout(5000)
        self.page.locator('[data-plugin-in-point-id="BOOK_IT_SIDEBAR"]').wait_for(state="visible")
        summary_locator = self.page.locator('[data-plugin-in-point-id="BOOK_IT_SIDEBAR"]')
        text = summary_locator.text_content().replace('\xa0', ' ')
        # logging.info(f"text is: {text}")

        price_per_night = int(text.split("night")[0].split()[-1].replace("₪", "").replace(",", ""))
        logging.info(f"extracted price: {price_per_night} from reservation card")

        checkin_str = text.split("Check-in")[1].split("Checkout")[0].strip()
        checkin_locator = self.page.get_by_test_id("change-dates-checkIn")
        expect(checkin_locator).to_have_text(checkin_str)
        logging.info(f"extracted check in date: {checkin_str} from reservation card")

        checkout_str = text.split("Checkout")[1].split("Guests")[0].strip()
        checkout_locator = self.page.get_by_test_id("change-dates-checkOut")
        expect(checkout_locator).to_have_text(checkout_str)
        logging.info(f"extracted check out date: {checkout_str} from reservation card")

        guests = text.split("Guests")[1].split("Reserve")[0]
        guest_locator = self.page.locator("#GuestPicker-book_it-trigger")
        expect(guest_locator).to_have_text(guests)
        logging.info(f"extracted guests: {guests} from reservation card")

    def do_reservation(self):
        reserve_btn = self.page.locator('button:has([data-button-content="true"]:has-text("Reserve"))').last
        logging.info("Clicking on Reserve button")
        if reserve_btn.is_visible():
            reserve_btn.click()
            self.page.wait_for_timeout(3000)
            expect(
                self.page.get_by_role("heading", name="Request to book").or_(
                    self.page.get_by_role("heading", name="Confirm and pay")
                )
            ).to_be_visible()

        # heading = self.page.locator('h1:text("Request to book")')
        input_phone = self.page.get_by_test_id('login-signup-phonenumber')
        if input_phone.is_visible():
            logging.info("'A' Page, can input phone, inputting..")
            input_phone.type("521231122")
        else:
            logging.info("'B' page, can't input phone")

