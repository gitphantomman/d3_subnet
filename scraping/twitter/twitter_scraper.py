import logging
from scraping.scraper import BaseScraper
from apify_client import ApifyClient
from dotenv import load_dotenv
import os
import asyncio
import sqlite3
from datetime import datetime
import asyncio
load_dotenv()
class TwitterScraper(BaseScraper):
    def __init__(self, save_path, apify_key):
        super().__init__(save_path)
        self.api_key = apify_key
        self.run_id = os.getenv("TwitterScraperActorId")
        # Assuming the existence of a Twitter API client setup
        self.client = self.setup_twitter_client(apify_key)
        self.actor = self.client.actor(self.run_id)
        self.fetched_items=[]
    def setup_twitter_client(self, apify_key):
        # Placeholder for Twitter API client setup
        # Replace with actual Twitter API client initialization
        logging.info("Setting up Twitter API client.")
        return ApifyClient(apify_key)

    def scrape(self, search_terms=["bittensor"]):
        """
        Implements the scraping logic specific to Twitter.
        This method should use the Twitter API client to fetch data.

        Returns:
            data (any): The scraped data from Twitter.
        """
        logging.info("Scraping data from Twitter.")
        run_input = {
            "searchTerms": search_terms,
            "searchMode": "live",
            "maxTweets": 200,
            "addUserInfo": True,
            "scrapeTweetReplies": True,
        }
        # Placeholder for scraping logic
        # Replace with actual data fetching from Twitter
        run = self.actor.call(run_input=run_input)
        dataset = self.client.dataset(run["defaultDatasetId"])
        items = dataset.iterate_items()
        self.fetched_items = []
        for item in items:
            self.fetched_items.append(item)
        return self.fetched_items

    
    async def search_by_urls(self, urls):
        results = []
        
        tasks = [self.scrape_single_url(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

    async def scrape_single_url(self, url):
        print(f"url: {url}")
        run_input = {
            "searchMode": "live",
            "maxTweets": 200,
            "maxRequestRetries": 3,
            "addUserInfo": True,
            # "scrapeTweetReplies": False,
            "maxTweets": 1,
            "urls": [url],
        }
        try:
            run = self.actor.call(run_input=run_input, timeout_secs=300)
            dataset = self.client.dataset(run["defaultDatasetId"])
            items = dataset.iterate_items()
            fetched_items = []
            for item in items:
                fetched_items.append(item)
            logging.info(f"✅ Fetched data for url: {url}")
        except Exception as e:
            fetched_items = []
            logging.error(f"Error fetching data for url: {url}, error: {e}")
        return fetched_items

    def save(self):
        """
        Implements the logic to save the scraped data.

        Args:
            data (any): The data to be saved.
        """
        # create data directory if it doesnt exist
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        self.conn = sqlite3.connect(self.save_path + 'twitter_data.db')

        # save fetched_items data to local sqlite database

        # Connect to SQLite database (or create it if it doesn't exist)

        c = self.conn.cursor()

        # Create table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS tweets
                     (id TEXT PRIMARY KEY, tweet_content TEXT, user_name TEXT, user_id TEXT, created_at TIMESTAMP, url TEXT, favourite_count INT, scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, image_urls TEXT)''')

        # Insert fetched items into the database
        for item in self.fetched_items:
            # Assuming 'item' is a dictionary with 'id', 'text', and 'user' keys
            tweet_id = item.get('id_str', 'N/A')
            tweet_content = item.get('full_text', 'N/A')
            user_name = str(item.get('user', 'N/A').get('screen_name', 'N/A'))
            user_id = str(item.get('user_id_str', 'N/A'))
            created_at = str(item.get('created_at', 'N/A'))
            url = str(item.get('url', 'N/A'))  # Converting user info to string for simplicity
            favourite_count = item.get('favorite_count', 'N/A')
            scraped_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get current time for scraped_at
            image_urls = item.get('entities', 'N/A').get('media', 'N/A')
            if image_urls != 'N/A':
                image_urls = [media['media_url_https'] for media in image_urls if media['type'] == 'photo']
            else:
                image_urls = 'N/A'
            # Inserting or ignoring on conflict to avoid duplicates
            c.execute("INSERT OR IGNORE INTO tweets (id, tweet_content, user_name, user_id, created_at, url, favourite_count, scraped_at, image_urls) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (tweet_id, tweet_content, user_name, user_id, created_at, url, favourite_count, scraped_at, str(image_urls)))

        # Commit the changes and close the connection
        self.conn.commit()
        logging.info(f"✅ Saved data to {self.save_path}twitter_data.db")
        # self.conn.close()

        

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    twitter_scraper = TwitterScraper("data/", os.getenv("APIFY_KEY"))
    twitter_scraper.scrape(["bittensor"])
    twitter_scraper.save()


