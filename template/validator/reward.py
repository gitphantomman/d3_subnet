# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# TODO(developer): Set your name
# Copyright © 2023 <your name>

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import torch
from typing import List
from datasets import load_dataset
import bittensor as bt
import neurons.indexing as indexing
from scraping.twitter import twitter_scraper
import os
from dotenv import load_dotenv
load_dotenv()
import asyncio
def reward(query: int, response: int) -> float:
    """
    Reward the miner response to the dummy request. This method returns a reward
    value for the miner, which is used to update the miner's score.

    Returns:
    - float: The reward value for the miner.
    """

    return 1.0 if response == query * 2 else 0


twitter_scraper = twitter_scraper.TwitterScraper("data/", os.getenv("APIFY_KEY"))
def get_rewards(
    self,
    responses
) -> torch.FloatTensor:
    """
    Returns a tensor of rewards for the given responses.

    Args:
    - responses : A list of responses from the miner.

    Returns:
    - torch.FloatTensor: A tensor of rewards for the given query and responses.
    """
    total_num_rows = 0
    spot_check_items = {}
    for response in responses:
        if response['commit'] is not None:
            # Download dataset
            try:
                repo_id = response['commit'].split("/datasets/")[-1]
                response['dataset'] = load_dataset(repo_id)
                response['num_rows'] = len(response['dataset']['train'])
                total_num_rows += response['num_rows']
            except Exception as e:
                bt.logging.error(f"Failed to load dataset from miner {response['uid']}")
                response['dataset'] = None
                response['num_rows'] = 0
        else:
            response['dataset'] = None
            response['num_rows'] = 0
    num_times = 1
    urls_for_spotcheck = []
    uids = []
    if total_num_rows > 100000:
        num_times = total_num_rows / 100000
    for response in responses:
        response['num_samples'] = int(response['num_rows'] / num_times)
        if response['dataset'] is not None:
            random_samples = response['dataset']['train'].shuffle().select(range(response['num_samples']))

            # Get a random spot check item
            random_spot_sample = response['dataset']['train'].shuffle().select(range(1))

            spot_check_items[response['uid']] = random_spot_sample[0]
            urls_for_spotcheck.append(random_spot_sample[0]['url'])
            uids.append(response['uid'])

            for row in random_samples:
                already_indexed = indexing.get_temp_indexing(row['id'])
                if indexing.get(row['id']) is not None:
                    continue
                if already_indexed is not None:
                    
                    if int(already_indexed.split("_")[0]) > response['block']:
                        indexing.save_temp_indexing(row['id'], str(response['block']) + "_" + str(response['uid']))
                else:
                    indexing.save_temp_indexing(row['id'], str(response['block']) + "_" + str(response['uid']))
            for row in response['dataset']['train']:
                indexing.save(row['id'], 1)
        else:
            random_samples = None
        response['samples'] = random_samples
    
    searched_results = asyncio.run(twitter_scraper.search_by_urls(urls_for_spotcheck))
        
    keys = indexing.get_all_temp_indexing_keys()
    
    counts = {}
    for key in keys:
        
        value = indexing.get_temp_indexing(key)
        block, uid = value.split("_")
        if uid not in counts:
            counts[uid] = 1
        else:
            counts[uid] += 1
        
    for i in range(len(searched_results)):
        if spot_check_items[uids[i]]['user_id'] != searched_results[i][0]['user_id_str']:
            bt.logging.info("Wrong tweet!")
            counts[str(uids[i])] = 0
        else: 
            bt.logging.info("Correct tweet!")
    # Remove temp indexing
    indexing.remove_temp_indexing()
    # Get all the reward results by iteratively calling your reward() function.
    return torch.FloatTensor(
        [counts.get(str(response['uid']), 0) ** 2 for response in responses]  # default value of 0 if key does not exist
    ).to(self.device)

