import logging
from datetime import datetime, timedelta

LOCATION = "Tel Aviv"
TODAY = datetime.today()
TOMORROW = TODAY + timedelta(days=1)
ADULTS = 2
CHILDREN = 1
GUESTS_FIRST_TASK = str(ADULTS)
GUESTS_SECOND_TASK = str(ADULTS+CHILDREN)


def test_first_task(pages):

    pages.home_page.search_bnb(
        location=LOCATION,
        checkin=TODAY,
        checkout=TOMORROW,
        adults=ADULTS
    )

    pages.home_page.validate_little_search(location=LOCATION,checkin=TODAY, checkout=TOMORROW, guests=GUESTS_FIRST_TASK)
    cards = pages.results_page.loop_over_results()
    highest_rating_cards = pages.results_page.filter_cards_by_rating(cards)
    logging.info("Highest rating cards:")
    pages.results_page.log_cards(highest_rating_cards)
    cheapest_cards = pages.results_page.filter_cards_by_price(cards)
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
    pages.home_page.validate_little_search(location=LOCATION,checkin=TODAY, checkout=TOMORROW,
                                           guests=GUESTS_SECOND_TASK)

    cards = pages.results_page.loop_over_results()
    highest_rating_cards = pages.results_page.filter_cards_by_rating(cards)
    logging.info("Got all highest rated cards, checking for most reviewed card:")
    selected = pages.results_page.get_most_reviewed_card(highest_rating_cards)
    logging.info("Navigating to best selected card")
    pages.page.goto(selected.url)
    pages.reservation_page.parse_and_validate_summary()
    pages.reservation_page.do_reservation()

