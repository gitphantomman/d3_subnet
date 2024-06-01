import logging
from scraper import BaseScraper
import pyarrow.csv as pv
from twscrape import API, Tweet
import json
import os
import datetime
import sqlite3

# from dotenv import load_dotenv
# import asyncio


# load_dotenv()


class TwitterScraperV3(BaseScraper):

    def __init__(
        self,
        save_path="data/",
        limit=1,
        kv=None,
        filePath="twacc.txt",
        fileHeaderFormat="username:password:email:email_password",
        saveToJsonFile=True
    ):
        super().__init__(save_path)
        logging.basicConfig(level=logging.INFO)

        self.api = API()  # or API("path-to.db") - default is `accounts.db`

        self.filePath = filePath
        self.fileHeaderFormat = fileHeaderFormat

        self.fetchedTweets:list[Tweet] = []
        self.limit = limit
        self.kv = kv
        self.saveToJsonFile = saveToJsonFile

    async def scrape(self, search_terms=["bittensor"]):
        """
        Implements the scraping logic specific to Twitter.
        This method should use the Twitter API client to fetch data.

        Returns:
            data (any): The scraped data from Twitter.
        """

        await self.api.pool.load_from_file(filepath=self.filePath, line_format=self.fileHeaderFormat)
        await self.api.pool.login_all()
        logging.info(f"Scraping data from Twitter.")

        for q in search_terms:
            # get list[Tweet]
            async for tweet in self.api.search(q, self.limit, self.kv):
                 # tweet is `Tweet` object
                self.fetchedTweets.append(tweet)

        logging.info(f"✅ Scraped.")

    def save(self):
        """
        Implements the logic to save the scraped data.

        Args:
            data (any): The data to be saved.
        """

        # if not exists then mkdir it
        if not os.path.exists(self.save_path):
            os.mkdir(self.save_path)

        # cd to path
        os.chdir(self.save_path)

        file = ""

        if (self.saveToJsonFile):
            jsons = []
            for tweet in self.fetchedTweets:
                tweet.dict()
                jsons.append(json.loads(tweet.json()))

            nowStr = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            file = "scraped_" + nowStr + ".json"
            with open(file, "w", encoding="utf-8") as f:
                json.dump(jsons, f, ensure_ascii=False, indent=4)

            logging.info(f"✅ Saved data to {self.save_path + "/" + file}")
        else:        
            file = 'scraped_twitter_data.db'
            
            try:
                # Connect to SQLite database (or create it if it doesn't exist)
                self.conn = sqlite3.connect(file)

                # Create a cursor object
                c = self.conn.cursor()

                # # Execute SQL DROP TABLE statement
                # c.execute("DROP TABLE IF EXISTS tweets")

                # Create table if it doesn't exist
                c.execute('''CREATE TABLE IF NOT EXISTS tweets
                                (id INTEGER PRIMARY KEY, tweet_content TEXT, url TEXT, date TIMESTAMP, replyCount INTEGER, retweetCount INTEGER, likeCount INTEGER, quoteCount INTEGER, viewCount INTEGER, user_id INTEGER, scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

                # Insert fetched items into the database
                for tweet in self.fetchedTweets:
                    # Inserting or ignoring on conflict to avoid duplicates
                    c.execute(
                        '''INSERT OR IGNORE INTO tweets (id, tweet_content, url, date, replyCount, retweetCount, likeCount, quoteCount, viewCount, user_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (tweet.id, tweet.rawContent, tweet.url, tweet.date, tweet.replyCount, tweet.retweetCount, tweet.likeCount, tweet.quoteCount, tweet.viewCount, tweet.user.id))

                # Commit the changes
                self.conn.commit()

                logging.info(f"✅ Saved data to {self.save_path + "/" + file}")

                # # Query the database
                # c.execute("SELECT * FROM tweets")

                # # Fetch all results and Print the results
                # for row in c.fetchall():
                #     print('=====', row)

            except Exception as e:
                logging.error(f"Error occurred: {e}")
                # Rollback the transaction
                self.conn.rollback()

            finally:
                # Close the connection
                self.conn.close()


# if __name__ == "__main__":
#     twitter_scraper = TwitterScraperV3(
#         save_path="data", limit=1, kv={"product": "Top"}, saveToJsonFile=False
#     )
#     asyncio.run(twitter_scraper.scrape(["elon musk"]))
#     twitter_scraper.save()
