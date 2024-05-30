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

import bittensor as bt
from common.utils.utilities import functools, run_in_subprocess
from common.validator.reward import get_rewards
from common.utils.uids import get_all_uids
from common.validator.system import Response



async def forward(self):
    """
    The forward function is called by the validator every time step.

    It is responsible for querying the network and scoring the responses.

    Args:
        self (:obj:`bittensor.neuron.Neuron`): The neuron object which contains all the necessary state for the validator.

    """
    if self.subtensor.block - self.last_block > self.config.num_blocks_for_validation:
        self.last_block = self.subtensor.block
        miners = get_all_uids(self)
        bt.logging.success("validator is getting commits from all miners")
        # get all miners from the metagraph

        # Sync before getting the latest commits from the miners
        responses = []
        miner_uids = []

        for miner in miners:
            miner_uids.append(miner['uid'])

            try:
                latest_commit = self.subtensor.get_commitment(netuid = self.config.netuid, uid = miner['uid'])
                bt.logging.success(f"Got the latest commit from miner {miner['uid']}")
                partial = functools.partial(bt.extrinsics.serving.get_metadata, self.subtensor, self.config.netuid, miner['hotkey'])
                metadata = run_in_subprocess(partial, 30)

                if self.subtensor.block - metadata['block'] < 300: # TODO: 
                    response = Response(commit=None, dataset=None, num_rows=0, uid=miner['uid'], block = None, real_num_rows = 0, wrong_tweet_exist = False)
                    responses.append(response)
                else:
                    response = Response(commit=latest_commit, dataset=None, num_rows=0, uid=miner['uid'], block = metadata['block'], real_num_rows = 0, wrong_tweet_exist = False)
                    responses.append(response)
                
            except Exception as e:
                bt.logging.debug(f"failed to get metadata from miner {miner['uid']}")
                response = Response(commit=None, dataset=None, num_rows=0, uid=miner['uid'], block = None, real_num_rows = 0, wrong_tweet_exist = False)
                responses.append(response)
                continue
        rewards = get_rewards(self, responses=responses)
        bt.logging.info(f"Scored responses: {rewards}")
        # Update the scores based on the rewards. You may want to define your own update_scores function for custom behavior.
        self.update_scores(rewards, miner_uids)


