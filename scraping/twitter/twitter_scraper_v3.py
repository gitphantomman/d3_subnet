import logging
from scraper import BaseScraper
from twscrape import API
import json
import os
import re

# from dotenv import load_dotenv
# import asyncio
# import os


# load_dotenv()


class TwitterScraperV3(BaseScraper):

    def __init__(
        self,
        save_path="data/",
        limit=1,
        kv=None,
        user=None,
        password=None,
        email=None,
        email_password=None,
    ):
        super().__init__(save_path)
        logging.basicConfig(level=logging.INFO)

        self.api = API()  # or API("path-to.db") - default is `accounts.db`

        self.user = user
        self.password = password
        self.email = email
        self.email_password = email_password

        self.fetched_items = []
        self.search_terms = ""
        self.limit = limit
        self.kv = kv

    async def scrape(self, search_terms=["bittensor"]):
        """
        Implements the scraping logic specific to Twitter.
        This method should use the Twitter API client to fetch data.

        Returns:
            data (any): The scraped data from Twitter.
        """
        self.search_terms = search_terms[0]

        await self.api.pool.add_account(
            self.user, self.password, self.email, self.email_password
        )
        await self.api.pool.login_all()
        logging.info(f"Scraping data from Twitter with 👤: [{self.user}].")

        # NOTE 1: gather is a helper function to receive all data as list, FOR can be used as well:
        async for tweet in self.api.search(
            self.search_terms, self.limit, self.kv
        ):  # list[Tweet]
            tweet.dict()
            self.fetched_items.append(
                json.loads(tweet.json())
            )  # tweet is `Tweet` object

        logging.info(f"✅ Scraped.")

    def save(self):
        """
        Implements the logic to save the scraped data.

        Args:
            data (any): The data to be saved.
        """

        if os.path.exists(self.save_path) == False:
            os.mkdir(self.save_path)
        os.chdir(self.save_path)

        file = re.sub(r"\s+", "_", self.search_terms) + ".json"
        with open(file, "w", encoding="utf-8") as f:
            json.dump(self.fetched_items, f, ensure_ascii=False, indent=4)

        logging.info(f"✅ Saved data to {self.save_path + "/" + file}")


# if __name__ == "__main__":
#     twitter_scraper = TwitterScraperV3(
#         "data",
#         1,
#         {"product": "Top"},
#         os.getenv("x_user"),
#         os.getenv("x_password"),
#         os.getenv("x_email"),
#         os.getenv("x_email_password"),
#     )
#     asyncio.run(twitter_scraper.scrape(["elon musk"]))
#     twitter_scraper.save()
