import logging
from datetime import datetime, timedelta

LOCATION = "Tel Aviv"
TODAY = datetime.today()
TOMORROW = TODAY + timedelta(days=1)
ADULTS = 2
CHILDREN = 1
GUESTS_FIRST_TASK = str(ADULTS)
GUESTS_SECOND_TASK = str(ADULTS+CHILDREN)
PHONE = "521231122"


def test_first_task(pages):

    pages.home_page.search_bnb(
        location=LOCATION,
        checkin=TODAY,
        checkout=TOMORROW,
        adults=ADULTS
    )

    all_cards,highest_rating_cards, cheapest_cards, _ = pages.results_page.loop_over_results()
    logging.info("Highest rating cards:")
    pages.results_page.log_cards(highest_rating_cards)
    logging.info("Cheapest cards:")
    pages.results_page.log_cards(cheapest_cards)


def test_second_task(pages):

    pages.home_page.search_bnb(
        location=LOCATION,
        checkin=TODAY,
        checkout=TOMORROW,
        adults=ADULTS,
        children=CHILDREN
    )

    _, _, _, highest_most_rated_card = pages.results_page.loop_over_results()
    logging.info("Navigating to best selected card")
    pages.page.goto(highest_most_rated_card.url)
    pages.reservation_page.parse_and_validate_summary()
    pages.reservation_page.do_reservation(phone=PHONE)

