import typing as tp
from bittensor import logging
from datasets import load_dataset


class Response(tp.TypedDict):
    commit: str
    dataset: tp.Any
    num_rows: int
    uid: int    
    block:int
    num_samples: int = 0
    real_num_rows: int = 0
    random_samples: tp.Any = None
    random_samples_for_spotcheck: tp.Any = None 
    wrong_tweet_exist: bool = False
    average_timestamp: float = 0.0
    rank_up_to_date: int = 0

def reward(responses: tp.List[Response]) -> tp.Any:
    """
    Returns a tensor of rewards for the given responses.

    Args:
    - responses : A list of responses from the miner.

    Returns:
    - torch.FloatTensor: A tensor of rewards for the given query and responses.
    """
    pass


def get_responses_dataset(responses):
    """ Load datasets for each response and count rows. """
    total_num_rows = 0
    for response in responses:
        commit = response.get('commit')
        if commit is None:
            response['dataset'] = None
            response['num_rows'] = 0
            continue

        repo_id = commit.split("/datasets/")[-1]

        if not repo_id:
            logging.error(f"Failed to extract repo_id from commit {commit}")
            response['dataset'] = None
            response['num_rows'] = 0
            continue

        try:
            dataset = load_dataset(repo_id, split='train')
            num_rows = len(dataset)
            response['dataset'] = dataset
            response['num_rows'] = num_rows
            total_num_rows += num_rows
        except Exception as e:
            logging.error(f"Failed to load dataset from commit {response['uid']}: {e}")
            response['dataset'] = None
            response['num_rows'] = 0

    return total_num_rows
