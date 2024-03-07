from abc import ABC, abstractmethod
import logging

class BaseScraper(ABC):
    """
    Abstract base class for scrapers. This class defines the basic structure and functionalities
    that all specific scraper subclasses (e.g., TwitterScraper, RedditScraper) should implement.
    It provides methods to scrape data and save it, but requires subclasses to implement the
    specific scraping logic.
    """

    def __init__(self, save_path):
        """
        Initializes the BaseScraper with a path to save the scraped data.

        Args:
            save_path (str): The file system path where scraped data should be saved.
        """
        self.save_path = save_path
        logging.basicConfig(level=logging.INFO)

    @abstractmethod
    def scrape(self, search_terms = ["bittensor"]):
        """
        Abstract method to scrape data from a specific source. Subclasses must implement this
        method to define how data is scraped.

        Returns:
            data (any): The scraped data, which could be of any type depending on the scraper.
        """
        pass

    @abstractmethod
    def save(self):
        """
        Abstract method to save the scraped data. Subclasses must implement this method to define
        how data is saved.

        Args:
            data (any): The data to be saved, which could be of any type depending on the scraper.
        """
        pass

    def run(self):
        """
        Main method to orchestrate the scraping and saving of data. It calls the `scrape` method
        to collect data and then saves it using the `save` method.
        """
        try:
            data = self.scrape()
            self.save(data)
            logging.info("Data scraping and saving completed successfully.")
        except Exception as e:
            logging.error(f"An error occurred during scraping or saving: {e}")
