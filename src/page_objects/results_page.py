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

    def loop_over_results(self):
        results = []
        highest_rated_cards = []
        cheapest_cards = []
        max_rating = 0
        max_reviews_for_top_rating = 0
        min_price = float('inf')
        highest_rated_most_reviewed = None
        page_number = 1

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
                        if not card_data:
                            continue
                        results.append(card_data)

                        if card_data.rating is not None:
                            if card_data.rating > max_rating:
                                logging.info(f"Found higher rating with {card_data.rating}, resetting list with it")
                                max_rating = card_data.rating
                                highest_rated_cards = [card_data]
                                highest_rated_most_reviewed = card_data if card_data.reviews is not None else None
                                max_reviews_for_top_rating = card_data.reviews if card_data.reviews is not None else 0

                            elif card_data.rating == max_rating:
                                highest_rated_cards.append(card_data)
                                logging.info("Found card with same rating as max rating, adding to list")
                                if card_data.reviews is not None and (highest_rated_most_reviewed is None or
                                                                      card_data.reviews > max_reviews_for_top_rating):
                                    logging.info(f"Found card amongst best rated with highest review count of "
                                                 f"{card_data.reviews}")
                                    highest_rated_most_reviewed = card_data
                                    max_reviews_for_top_rating = card_data.reviews

                        if card_data.price < min_price:
                            logging.info(f"Found cheaper card with price of {card_data.price}, updating list")
                            min_price = card_data.price
                            cheapest_cards = [card_data]
                        elif card_data.price == min_price:
                            logging.info(f"Found  card with same minimum price, adding to list")
                            cheapest_cards.append(card_data)

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

        return results,highest_rated_cards, cheapest_cards, highest_rated_most_reviewed

    def log_cards(self, cards: List[Card]):
        for c in cards:
            logging.info(f"Rating: {c.rating} Price: {c.price} Reviews: {c.reviews} Url: {c.url}")
