# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
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

import asyncio
import torch
from typing import List
from datasets import load_dataset
import bittensor as bt
import neurons.indexing as indexing
from scraping.twitter import twitter_scraper
from datetime import datetime
from scraping.twitter import twitter_scraper_v2
import os
from dotenv import load_dotenv
from common.validator.system import Response
load_dotenv()

# twitter_scraper = twitter_scraper.TwitterScraper("data/", os.getenv("APIFY_KEY"))
twitter_scraper_v2 = twitter_scraper_v2.TwitterScraperV2(apify_key = os.getenv("APIFY_KEY"))

def get_rewards(
    self,
    responses: List[Response],
) -> torch.FloatTensor:
    """
    Returns a tensor of rewards for the given responses.

    Args:
    - responses : A list of responses from the miner.

    Returns:
    - torch.FloatTensor: A tensor of rewards for the given query and responses.
    """
    total_num_rows = 0
    all_spot_check_urls = []
    valid_uid_list = []
    for response in responses:
        if response['commit'] is not None:
            # Download dataset
            try:
                repo_id = response['commit'].split("/datasets/")[-1]
                response['dataset'] = load_dataset(repo_id)
                response['num_rows'] = len(response['dataset']['train'])
                total_num_rows += response['num_rows']
            except Exception as e:
                bt.logging.debug(f"Failed to load dataset from miner {response['uid']} : {e}")
                response['dataset'] = None
                response['num_rows'] = 0
            
        else:
            response['dataset'] = None
            response['num_rows'] = 0
    devide = 1
    if total_num_rows > 100000:
        devide = total_num_rows / 100000
    
    try:
        for response in responses:
            # Get sampling size
            response['num_samples'] = int(response['num_rows'] / devide)
            if response['dataset'] is not None:
                # Get random samples
                if devide == 1:
                    response['random_samples'] = response['dataset']['train']
                else:
                    response['random_samples'] = response['dataset']['train'].shuffle().select(range(response['num_samples']))
                # Get random spot check items
                if response['num_rows'] > self.config.num_spot_check_items_per_response:
                    response['random_samples_for_spotcheck'] = response['dataset']['train'].shuffle().select(range(self.config.num_spot_check_items_per_response))
                else:
                    response['random_samples_for_spotcheck'] = response['dataset']['train']
                    
                # Get spot check score
                all_spot_check_urls.append(response['random_samples_for_spotcheck']['url'])
                valid_uid_list.append(response['uid'])
                # check samples already indexed and calculate the number of new rows
                timestamp_sum = 0
                for row in response['random_samples']:
                    already_indexed = indexing.get_temp_indexing(row['id'])
                    if indexing.get(row['id']) is not None:
                        continue
                    if already_indexed is not None:
                        if int(already_indexed.split("_")[0]) > response['block']:
                            indexing.save_temp_indexing(row['id'], str(response['block']) + "_" + str(response['uid']))
                    else:
                        indexing.save_temp_indexing(row['id'], str(response['block']) + "_" + str(response['uid']))
                    indexing.save(row['id'], 1)
                    timestamp_sum += to_timestamp(row['created_at'])
                response['average_timestamp'] = timestamp_sum / len(response['random_samples'])
            else:
                response['random_samples'] = None
    except Exception as e:
        bt.logging.error(f"Failed to get random samples from dataset : {e}")
        return torch.FloatTensor([0] * len(responses)).to(self.device)
    
    searched_results = asyncio.run(twitter_scraper_v2.search_by_urls(all_spot_check_urls))

    keys = indexing.get_all_temp_indexing_keys()
    for key in keys:
        value = indexing.get_temp_indexing(key)
        block, uid = value.split("_")
        responses[int(uid)]['real_num_rows'] += 1

    # check timestamp
    for i, uid in enumerate(valid_uid_list):
        # rank valid_uid_list by average_timestamp
        for j in range(i+1, len(valid_uid_list)):
            if responses[uid]['average_timestamp'] < responses[valid_uid_list[j]]['average_timestamp']:
                valid_uid_list[i], valid_uid_list[j] = valid_uid_list[j], valid_uid_list[i]
    

    for i, uid in enumerate(valid_uid_list):
        cnt = 0
        
        spot_check_list = responses[uid]['random_samples_for_spotcheck']
        cmp_item_list = searched_results[i]
        for item in spot_check_list:
            
            # find this id in cmp_item_list
            for cmp_item in cmp_item_list:
                try:
                    if item['id'] == cmp_item['id']:
                        if item['tweet_content'] != cmp_item['text']:
                            cnt += 1
                            print("Wrong tweet!")
                        else:
                            print("Correct tweet!")
             
                except Exception as e:
                    cnt += 1
                    bt.logging.error(f"Failed to compare spot check items: {e}")
        if cnt >= int(self.config.num_spot_check_items_per_response / 2):
            responses[uid]['real_num_rows'] = 0

        responses[uid]['wrong_tweet_cnt'] = cnt
        responses[uid]['rank_up_to_date'] = i
        

    print(responses)
    # Remove temp indexing
    indexing.remove_temp_indexing()
    return torch.FloatTensor(
        [response['real_num_rows'] ** 2 * ((response['rank_up_to_date'] + 1) / (len(valid_uid_list) + 1)) / (response['wrong_tweet_cnt'] + 1) for response in responses]
    ).to(self.device)


# this function converts a tweet date string to a timestamp
def to_timestamp(date_string:str):
    # Define the format of the date string
    date_format = "%a %b %d %H:%M:%S %z %Y"

    # Parse the string into a datetime object
    date_object = datetime.strptime(date_string, date_format)
    # print(f"date_object: {date_object}")

    # Convert the datetime object to a timestamp
    timestamp = date_object.timestamp()
    return timestamp