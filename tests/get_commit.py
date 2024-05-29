import bittensor as bt
subtensor = bt.subtensor(network = "test")
latest_commit = subtensor.get_commitment(netuid = 18, uid = 43)
print(latest_commit)