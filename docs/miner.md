# Miner

`Miners periodically scrape according to their strategies and store it in their local database.
They publish to their Huggingface dataset once in the next 100 blocks and commit the link to the subtensor chain.
Next, initialize their local database and build the database again for the next commit.
Since miners do not receive queries and there is no limit to their number, we can obtain infinite data depending on the miner's capabilities.
Miners must have a good strategy as their rewards increase exponentially depending on their ranking.
The basic indicators are the amount of non-redundant data and if the data was correct.
If data overlaps, the miner who commits first wins, so miners must commit as much of the latest data as often as possible. The minimum commit cycle is 100 blocks.`

## Mining Requirements

Miners must have adequate disk space to temporarily store data in SQLite format before committing it.
It is recommended to have at least 30GB of disk space.

## Configuration

Please create a `.env` file based on the `.env.example` template.

```python
TwitterScraperActorId=heLL6fUofdPgRXZie
TwitterScraperV2ActorId=61RPP7dywgiy0JPD0
APIFY_KEY=
HF_TOKEN=
MAIN_REPO_ID=bittensor-dataset/twitter-text-dataset
```
You require an Apify API key to scrape tweets or other data. (Please upgrade your apify key plan here: https://console.apify.com/billing/subscription?openSubscriptionWizard=1)

Additionally, you need a write-access token from Huggingface to publish your own dataset. (You can get your token from here: https://huggingface.co/settings/tokens)

Please configure the miner by completing the `.env` file.

## Running Miner

### Activate venv
```bash
. my-env/bin/activate
```

### Running the miner script

```bash
python neurons/miner.py --subtensor.network finney --netuid 6 --wallet.name default --wallet.hotkey default --axon.port 8091 --logging.debug
```

### Extended Running CLI
```bash
python neurons/miner.py --subtensor.network finney --netuid 6 --wallet.name default --wallet.hotkey default --axon.port 8091 --logging.debug --num_blocks_for_commit 200 --scrape_interval 120 --db_directory data/ --twitter_scraper_version 1
```


-    `--wallet.name`: Specify the name of the cold key holding the hotkey linked to your miner.
-    `--wallet.hotkey`: Enter the name of the hotkey registered to your miner.
-    `--num_blocks_for_commit`: Define the count of blocks until the next commit.
-    `--scrape_interval`: Set the time interval (in seconds) for scraping operations.
-    `--db_directory`: Indicate the local directory path for storing temporary data sets.
-    `--auto_update`: If this is True, miners will update their repo automatically. The default config value is `False`.
-    `--twitter_scraper_version`: Version of Twitter Scraper to user in apify. (1, 2 or 3)

## Customize your miner

To maximize your rewards, it's essential to customize your miner. There are three different scrapers available:

1. The first two scrapers use Apify.
2. The third scraper utilizes Twitter accounts.

For more details on the non-Apify scraper, refer to the [Twitter scraper Guide](./non_apify.md). To customize the Apify scrapers, you can modify the `run_input` configuration variable within the scraper script.