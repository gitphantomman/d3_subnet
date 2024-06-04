# TWScraping

A library that supports scraping tweet data from x.com and saving it into an sqlite3 database.
This library uses and customizes from twscrape by the author [vladkens](https://github.com/vladkens/twscrape).

## Prospects

The library fetches tweets using the GraphQL Twitter API, making it very easy to use and customize.
The system scrapes content from Twitter using the miners' accounts, it is not dependent on any other service.

## Consequences

N/A

## Setup

```python
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e .
python3 -m pip install -r requirements.txt
```

## Running

```python
...
import asyncio
twitter_scraper = TwitterScraperV3(
    save_path="data/", limit=50, kv={"product": "Top"}
)
asyncio.run(
    twitter_scraper.scrape(
        [
            TwitterQueryBuilder()
            .anyWords("elon musk")
            .fromDate(datetime.date(2024, 1, 1))
            .build()
        ]
    )
)
twitter_scraper.save()
...
```

## Configuration

`TwitterScraperV3` accepts the following input parameters:

- `save_path (string)`: the path to save data after scraping
- `limit (number)`: limit the number of tweets fetched per account.
- `kv (object{key: value})`: specify additional options when fetching tweets, change search tab (product), can be: Top, Latest (default), Media (e.g., `{'product': 'Top'}`) 
- `filePath (string)`: the path to the file containing account information to fetch tweets
- `fileHeaderFormat (string)`: specify the format of account information in filePath (e.g., `username:password:email:email_password`)

When using the `scrape` function within `TwitterScraperV3`, you'll need to use `TwitterQueryBuilder` to build custom queries for fetching tweets.

The `TwitterQueryBuilder` provides the following helper functions:

- `tweetUrl(url: string)` => Specify a tweet URL (e.g., `https://x.com/alertarojanot/status/1797051547311829246`).
- `tweetId(tweetId: string)` => Specify a tweet ID (e.g., `1797051547311829246` for `https://x.com/{username}/status/{tweetId}`).
- `words(word: string)` => Search for tweets containing specific words.
- `exactWords(word: string)` => Search for exact matches of a word.
- `anyWords(word: string)` => Search for tweets containing any characters from a word.
- `hashtags(word: string)` => Search for tweets with specific hashtags.
- `fromAccount(word: string)` => Search for tweets from a specific account.
- `toAccount(word: string)` => Search for tweets directed at a specific account.
- `mentionAccount(word: string)` => Search for tweets mentioning a specific account.
- `fromDate(date: Date)` => Search for tweets from a specific date.
- `toDate(date: Date)` => Search for tweets up to a specific date.
- `build()` => **Important**! Always include this function at the end when using `TwitterQueryBuilder` to create your desired query.