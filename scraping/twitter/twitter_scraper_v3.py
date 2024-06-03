import logging
from scraping.scraper import BaseScraper
from twscrape import API, Tweet
import os
import datetime
import sqlite3


class TwitterScraperV3(BaseScraper):

    def __init__(
        self,
        save_path="data/",
        limit=10,
        kv={"product": "Latest"},
        filePath="twacc.txt",
        fileHeaderFormat="username:password:email:email_password",
    ):
        super().__init__(save_path)
        logging.basicConfig(level=logging.INFO)

        self.api = API()

        self.filePath = filePath
        self.fileHeaderFormat = fileHeaderFormat

        self.fetchedTweets: list[Tweet] = []
        self.limit = limit
        self.kv = kv

    async def scrape(self, search_terms=["bittensor"]):
        """
        Implements the scraping logic specific to Twitter.
        This method should use the Twitter API client to fetch data.

        Returns:
            data (any): The scraped data from Twitter.
        """

        await self.api.pool.load_from_file(
            filepath=self.filePath, line_format=self.fileHeaderFormat
        )
        await self.api.pool.login_all()
        logging.info(f"Scraping data from Twitter.")

        logging.info(f"search_terms: {search_terms}")
        for q in search_terms:
            # get list[Tweet]
            async for tweet in self.api.search(q, self.limit, self.kv):
                # tweet is `Tweet` object
                self.fetchedTweets.append(tweet)

        logging.info(f"✅ Scraped {len(self.fetchedTweets)} tweets.")

    def save(self):
        """
        Implements the logic to save the scraped data.

        Args:
            data (any): The data to be saved.
        """

        try:
            # create data directory if it doesnt exist
            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)

            self.conn = sqlite3.connect(self.save_path + "twitter_data.db")
            c = self.conn.cursor()

            # Create table if it doesn't exist
            c.execute(
                """CREATE TABLE IF NOT EXISTS tweets
                            (id TEXT PRIMARY KEY, tweet_content TEXT, user_name TEXT, user_id TEXT, created_at TIMESTAMP, url TEXT, favourite_count INT, scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, image_urls TEXT)"""
            )

            # Insert fetched items into the database
            for tweet in self.fetchedTweets:
                imgUrls = [photo.url for photo in tweet.media.photos]
                # Inserting or ignoring on conflict to avoid duplicates
                c.execute(
                    """INSERT OR IGNORE INTO tweets (id, tweet_content, user_name, user_id, created_at, url, favourite_count, image_urls)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        tweet.id,
                        tweet.rawContent,
                        tweet.user.username,
                        tweet.user.id,
                        tweet.date,
                        tweet.url,
                        tweet.likeCount,
                        str(imgUrls),
                    ),
                )

            # Commit the changes
            self.conn.commit()

            logging.info(f"✅ Saved data to {self.save_path}twitter_data.db")

        except Exception as e:
            logging.error(f"Error occurred: {e}")
            if hasattr(self, "conn") and self.conn is not None:
                # Rollback the transaction
                self.conn.rollback()

        finally:
            if hasattr(self, "conn") and self.conn is not None:
                # Close the connection
                self.conn.close()


class TwitterQueryBuilder:
    def __init__(self):
        self.__query = []

    def tweetUrl(self, url=""):
        # https://x.com/alertarojanot/status/1797051547311829246 => https://x.com/{username}/status/{tweetId}
        tweetUrl = url.split("/")[-3:]
        # username = tweetUrl[-3]
        tweetId = tweetUrl[-1]
        return self.tweetId(tweetId)

    def tweetId(self, tweetId=""):
        # tweetId: number
        return self.words(tweetId)

    def words(self, word=""):
        # cats dogs => cats dogs
        self.__query.append(word)
        return self

    def exactWords(self, word=""):
        # cats dogs => "cats dogs"
        self.__query.append(f'"{word}"')
        return self

    def anyWords(self, word=""):
        # cats dogs => (cats OR dogs)
        self.__query.append(f"({self.__multiWords(word)})")
        return self

    def hashtags(self, word=""):
        # cats dogs => (#cats OR #dogs)
        self.__query.append(f"({self.__multiWords(word, '#')})")
        return self

    def fromAccount(self, word=""):
        # elon => (from:elon)
        self.__query.append(f"(from:{word})")
        return self

    def toAccount(self, word=""):
        # elon => (to:elon)
        self.__query.append(f"(to:{word})")
        return self

    def mentionAccount(self, word=""):
        # elon => (@elon)
        self.__query.append(f"(@{word})")
        return self

    def fromDate(self, _date=datetime.date):
        # 2024-01-01 => since:2024-02-01
        self.__query.append(f"since:{_date.strftime('%Y-%m-%d')}")
        return self

    def toDate(self, _date=datetime.date):
        # 2024-01-01 => until:2024-01-01
        self.__query.append(f"until:{_date.strftime('%Y-%m-%d')}")
        return self

    def build(self):
        return " ".join(self.__query)

    def __multiWords(self, word="", prefix=""):
        return " OR ".join([f"{prefix}{str}" for str in word.split(" ")])


# if __name__ == "__main__":
#     import asyncio
#     twitter_scraper = TwitterScraperV3(
#         save_path="data/", limit=50, kv={"product": "Top"}
#     )
#     asyncio.run(
#         twitter_scraper.scrape(
#             [
#                 TwitterQueryBuilder()
#                 .anyWords("elon musk")
#                 .fromDate(datetime.date(2024, 1, 1))
#                 .build()
#             ]
#         )
#     )
#     twitter_scraper.save()
