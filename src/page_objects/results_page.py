import logging
from dataclasses import dataclass
from typing import Optional, List

from playwright.sync_api import Page, Locator


@dataclass
class Card:
    rating: Optional[float]
    price: float
    reviews: Optional[int]
    url: str


class ResultsPage:
    def __init__(self, page: Page):
        self.page = page
        self.card = self.page.locator('[itemprop="itemListElement"]')
        self.next_btn = self.page.locator('a[aria-label="Next"]')
        self.next_btn_stop = page.locator('button[aria-disabled="true"][aria-label="Next"]')

    def parse_card(self, card: Locator) -> Optional[Card]:
        try:
            card_text = card.text_content()

            logging.debug(f"Raw card text: {card_text}")

            price = float(card_text.split('total₪')[-1].split(' ')[0].replace(',', ''))

            rating = None
            reviews = None

            if 'rating' in card_text.lower():
                try:
                    rating = float(card_text.split('breakdown')[-1].split(' ')[0].replace("'", ''))
                except (ValueError, IndexError):
                    logging.debug("Could not parse rating")

            if 'review' in card_text.lower():
                try:
                    reviews = int(card_text.split('rating, ')[-1].split(' ')[1])
                except (ValueError, IndexError):
                    logging.debug("Could not parse reviews")

            url = None
            try:
                url_element = card.locator('a[href^="/rooms/"]').first
                url = url_element.get_attribute('href')
                if url and not url.startswith('http'):
                    url = "https://www.airbnb.com" + url
            except Exception as e:
                logging.debug(f"Could not get URL: {str(e)}")

            logging.info(f'Card loaded with rating: {rating} price: {price} reviews: {reviews} url: {url}')
            return Card(rating=rating, price=price, reviews=reviews, url=url)

        except Exception as e:
            logging.error(f"Bad card - skipped. Error: {str(e)}")
            return None

    def loop_over_res(self) -> List[Card]:
        results = []
        page_number = 1
        self.card.first.wait_for(state="visible", timeout=10000)
        self.card.last.wait_for(state="visible", timeout=10000)
        while True:
            logging.info(f"Processing page {page_number}")

            try:
                self.card.first.wait_for(state="visible", timeout=10000)
                self.card.last.wait_for(state="visible", timeout=10000)

                cards = self.card.all()
                logging.info(f"Found {len(cards)} cards on page {page_number}")

                for idx, c in enumerate(cards):
                    try:
                        logging.debug(f"Processing card {idx + 1} of {len(cards)}")
                        card_data = self.parse_card(c)
                        if card_data:
                            results.append(card_data)
                    except Exception as e:
                        logging.error(f"Error processing card {idx + 1}: {str(e)}")

                logging.debug("Checking for next page...")
                if self.next_btn_stop.is_hidden():
                    logging.info(f"Moving to page {page_number + 1}")
                    self.next_btn.click()

                    page_number += 1
                else:
                    logging.info("Reached last page")
                    break

            except Exception as e:
                logging.error(f"Error processing page {page_number}: {str(e)}")
                break

        logging.info(f"Total cards collected: {len(results)}")
        return results

    def filter_cards_by_rating(self, cards: List[Card]) -> List[Card]:
        rated_cards = list(filter(lambda c: c.rating is not None, cards))
        max_rating = max(map(lambda c: c.rating, rated_cards))
        logging.info(f"max rating card found with rating of: {max_rating}")
        top_rated_cards = list(filter(lambda c: c.rating == max_rating, rated_cards))
        return top_rated_cards

    def filter_cards_by_price(self, cards: List[Card]) -> List[Card]:
        min_price = min(map(lambda c: c.price, cards))
        logging.info(f"minimum price card found with price of: {min_price}")
        cheapest_cards = list(filter(lambda c: c.price == min_price, cards))
        return cheapest_cards

    def log_cards(self, cards: List[Card]):
        for c in cards:
            logging.info(f"Rating: {c.rating} Price: {c.price} Reviews: {c.reviews} Url: {c.url}")

    def get_most_reviewed_card(self, cards: List[Card]) -> Card:
        reviewed_cards = [c for c in cards if c.reviews is not None]
        most_reviewed = max(reviewed_cards, key=lambda c: c.reviews)
        logging.info(f"Amongst the highest rating options, selected highest review count option with rating of "
                     f"{most_reviewed.rating} and review count of: {most_reviewed.reviews}")
        return most_reviewed
