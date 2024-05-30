# Validator

`The following is the role of the validator:
Validators obtain the most recent commitments of current miners once every 250 blocks and obtain the HF dataset link and commit timestamp from them.
Next, download the miners' datasets and create an indexing table by removing duplicates to assign scores to miners.
At this time, if a duplicate appears, it is treated as belonging to the miner that committed first.
After this is over, the remaining number becomes the actual number miners scraped during 200 blocks.
One important thing is that when we talk about duplication, we consider not only duplication between miners, but also duplication with data in the basic database currently in the Bittensor Dataset Hub. For this, validators have a Redis database that stores only archived twitter_ids, and synchronize with the default indexing database provided by the owner when the validator starts or restarts.
After this duplicate removal process is completed, the miner's score is calculated and set_weights by considering other factors such as time and data accuracy. Additionally, validators give dishonest miners (e.g., tweet id and content that do not match) a score of 0 and notify the owner. Then, when the owner creates the dataset, he saves labor by excluding those miners.
For reference, if there is a lot of data from miners between 250 blocks, samples are selected for verification. Additionally, we factor into the Miner score how up-to-date the information is.`

# Validator Requirements

Validators will need high capacity RAM for building Redis indexing table.
It is recommended to have at least 40GB of RAM space and 500GB of storage.

Also, validators will need apify API token for spotcheck. (https://console.apify.com/billing/subscription)

## Configuration

Please create a `.env` file based on the `.env.example` template.

```python
TwitterScraperActorId=heLL6fUofdPgRXZie
TwitterScraperV2ActorId=61RPP7dywgiy0JPD0
APIFY_KEY=
HF_TOKEN=
MAIN_REPO_ID=bittensor-dataset/twitter-text-dataset
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=
```
Please configure the miner by completing the `.env` file.

## Install Redis (ubuntu)
- Prerequisites
```bash
sudo apt install lsb-release curl gpg
```
- Add the repo to the apt index, update it, and then install:
```bash
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list

sudo apt-get update
sudo apt-get install redis
```

To get more details, please visit the [Redis documentation](https://redis.io/docs/install/).


## Running Validator

### Activate venv
```bash
. my-env/bin/activate
```

### Running the validator script

```bash
python neurons/validator.py --subtensor.network local --netuid 10 --wallet.name default --wallet.hotkey default --axon.port 8092 --logging.debug
```

### Extened Running CLI

```bash
python neurons/validator.py --subtensor.network local --netuid 10 --wallet.name default --wallet.hotkey default --axon.port 8092 --logging.debug --num_blocks_for_validation 250 --num_spot_check_items_per_response 20
```

-    `--wallet.name`: Specify the name of the cold key holding the hotkey linked to your miner.
-    `--wallet.hotkey`: Enter the name of the hotkey registered to your miner.
-    `--num_blocks_for_validation`: Define the count of blocks until the next validation.
-    `--auto_update`: If this is True, validators will update their repo automatically. The default config value is `True`.
-    `--num_spot_check_items_per_response`: Number of spot check items per response.
