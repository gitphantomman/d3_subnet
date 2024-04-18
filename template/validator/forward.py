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

import bittensor as bt
from template.utils.utilities import functools, run_in_subprocess
from template.protocol import Dummy
from template.validator.reward import get_rewards
from template.utils.uids import get_random_uids, get_all_uids
from bittensor import logging
import os
from datasets import load_dataset
import indexing


def sync_last_indexed():
    repo_id = os.getenv("MAIN_REPO_ID")
    try:
        dataset = load_dataset(repo_id, split='train', columns=['id'])
        pipeline = indexing.r.pipeline(transaction=False)
        batch_size = 10000
        total_rows = 0
        indexed_cnt = 0
        last_indexed = indexing.get(f"{repo_id}:last", None)

        for row in dataset:
            pipeline.setnx(row['id'], 1)
            total_rows += 1

            if total_rows % batch_size == 0:
                try:
                    indexed_results = pipeline.execute()
                    indexed_cnt += sum(indexed_results)
                except Exception as e:
                    logging.error(f"Failed to index the dataset: {e}")
                    continue
                logging.info(f"Processed {total_rows} rows, Indexed {indexed_cnt} new rows.")

        if total_rows % batch_size != 0:
            indexed_results = pipeline.execute()
            indexed_cnt += sum(indexed_results)

        last_indexed = dataset[-1]['id']
        logging.info(f"Total processed rows: {total_rows}, Indexed {indexed_cnt} rows.")

        last_indexed = dataset[-1]['id']
        flag_key = f"{repo_id}:last"
        indexing.r.set(flag_key, last_indexed)
        logging.success(f"Successfully indexed the dataset. Last indexed key: {flag_key}")
    except Exception as e:
        logging.error(f"Failed to index the dataset: {e}")


async def forward(self):
    """
    The forward function is called by the validator every time step.

    It is responsible for querying the network and scoring the responses.

    Args:
        self (:obj:`bittensor.neuron.Neuron`): The neuron object which contains all the necessary state for the validator.

    """
    if self.subtensor.block - self.last_block > self.config.num_blocks_for_validation:
        miners = get_all_uids(self)
        bt.logging.success("validator is getting commits from all miners")
        # get all miners from the metagraph

        # Sync before getting the latest commits from the miners
        sync_last_indexed()
        responses = []
        miner_uids = []

        for miner in miners:
            miner_uids.append(miner['uid'])

            try:
                latest_commit = self.subtensor.get_commitment(netuid = self.config.netuid, uid = miner['uid'])
                bt.logging.success(f"Got the latest commit from miner {miner['uid']}")
                partial = functools.partial(bt.extrinsics.serving.get_metadata, self.subtensor, self.config.netuid, miner['hotkey'])
                metadata = run_in_subprocess(partial, 30)
                if self.subtensor.block - metadata['block'] > 300:
                    responses.append({'uid': miner['uid'], 'hotkey': miner['hotkey'], 'commit': None, 'block': None})
                # print(f"latest_commit: {latest_commit} block: {metadata['block']}")
                else:
                    responses.append({'uid': miner['uid'], 'hotkey': miner['hotkey'], 'commit': latest_commit, 'block': metadata['block']})
                # responses.append({'uid': miner['uid'], 'hotkey': miner['hotkey'], 'commit': latest_commit, 'block': metadata['block']})
            except Exception as e:
                bt.logging.error(f"failed to get metadata from miner {miner['uid']}")
                responses.append({'uid': miner['uid'], 'hotkey': miner['hotkey'], 'commit': None, 'block': None})
                continue
        bt.logging.success("Got all commits from miners")
        rewards = get_rewards(self, responses=responses)
        self.last_block = self.subtensor.block
        bt.logging.info(f"Scored responses: {rewards}")
        # Update the scores based on the rewards. You may want to define your own update_scores function for custom behavior.
        self.update_scores(rewards, miner_uids)


