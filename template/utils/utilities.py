import functools
import multiprocessing
import os
from typing import Any, Optional, Tuple
import bittensor as bt



def assert_registered(wallet: bt.wallet, metagraph: bt.metagraph) -> int:
    """Asserts the wallet is a registered miner and returns the miner's UID.

    Raises:
        ValueError: If the wallet is not registered.
    """
    if wallet.hotkey.ss58_address not in metagraph.hotkeys:
        raise ValueError(
            f"You are not registered. \nUse: \n`btcli s register --netuid {metagraph.netuid}` to register via burn \n or btcli s pow_register --netuid {metagraph.netuid} to register with a proof of work"
        )
    uid = metagraph.hotkeys.index(wallet.hotkey.ss58_address)
    bt.logging.success(
        f"You are registered with address: {wallet.hotkey.ss58_address} and uid: {uid}"
    )

    return uid


# def validate_hf_repo_id(repo_id: str) -> Tuple[str, str]:
#     """Verifies a Hugging Face repo id is valid and returns it split into namespace and name.

#     Raises:
#         ValueError: If the repo id is invalid.
#     """

#     if not repo_id:
#         raise ValueError("Hugging Face repo id cannot be empty.")

#     if not 3 < len(repo_id) <= ModelId.MAX_REPO_ID_LENGTH:
#         raise ValueError(
#             f"Hugging Face repo id must be between 3 and {ModelId.MAX_REPO_ID_LENGTH} characters. Got={repo_id}"
#         )

#     parts = repo_id.split("/")
#     if len(parts) != 2:
#         raise ValueError(
#             f"Hugging Face repo id must be in the format <org or user name>/<repo_name>. Got={repo_id}"
#         )

#     return parts[0], parts[1]


# def get_hf_url(model_metadata: ModelMetadata) -> str:
#     """Returns the URL to the Hugging Face repo for the provided model metadata."""
#     return f"https://huggingface.co/{model_metadata.id.namespace}/{model_metadata.id.name}/tree/{model_metadata.id.commit}"


def _wrapped_func(func: functools.partial, queue: multiprocessing.Queue):
    try:
        result = func()
        queue.put(result)
    except (Exception, BaseException) as e:
        # Catch exceptions here to add them to the queue.
        queue.put(e)


def run_in_subprocess(func: functools.partial, ttl: int, mode="fork") -> Any:
    """Runs the provided function on a subprocess with 'ttl' seconds to complete.

    Args:
        func (functools.partial): Function to be run.
        ttl (int): How long to try for in seconds.

    Returns:
        Any: The value returned by 'func'
    """
    ctx = multiprocessing.get_context(mode)
    queue = ctx.Queue()
    process = ctx.Process(target=_wrapped_func, args=[func, queue])

    process.start()

    process.join(timeout=ttl)

    if process.is_alive():
        process.terminate()
        process.join()
        raise TimeoutError(f"Failed to {func.func.__name__} after {ttl} seconds")

    # Raises an error if the queue is empty. This is fine. It means our subprocess timed out.
    result = queue.get(block=False)

    # If we put an exception on the queue then raise instead of returning.
    if isinstance(result, Exception):
        raise result
    if isinstance(result, BaseException):
        raise Exception(f"BaseException raised in subprocess: {str(result)}")

    return result


def get_version(filepath: str) -> Optional[int]:
    """Loads a version from the provided filepath or None if the file does not exist.

    Args:
        filepath (str): Path to the version file."""
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            line = f.readline()
            if line:
                return int(line)
            return None
    return None


def save_version(filepath: str, version: int):
    """Saves a version to the provided filepath."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write(str(version))


def move_file_if_exists(src: str, dst: str) -> bool:
    """Moves a file from src to dst if it exists.

    Returns:
        bool: True if the file was moved, False otherwise.
    """
    if os.path.exists(src) and not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        os.replace(src, dst)
        return True
    return False
