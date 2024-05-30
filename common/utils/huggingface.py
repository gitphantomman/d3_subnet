import sqlite3
import pandas as pd
from datasets import Dataset
from huggingface_hub import HfApi, HfFolder
import os
from dotenv import load_dotenv
import bittensor as bt
import traceback
load_dotenv()
import time
def create_hf_dataset_from_sqlite(subtensor, wallet, netuid, db_path, table_name, dataset_name, dataset_description):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    # Convert the specified table to a pandas DataFrame
    df = pd.read_sql_query(f"SELECT * from {table_name}", conn)
    # Close the connection to the database
    conn.close()
    # Convert the pandas DataFrame to a Hugging Face dataset
    hf_dataset = Dataset.from_pandas(df)
    # Get the Hugging Face token from the environment variable
    hf_token = os.getenv("HF_TOKEN")
    # Authenticate with the Hugging Face Hub
    api = HfApi()
    # Push the dataset to the Hugging Face Hub
    url = api.create_repo(token=hf_token, repo_id=dataset_name, private=False, repo_type="dataset")
    no_bug = False
    while no_bug is False:
        try:
            subtensor.commit(wallet, netuid, url)
            bt.logging.success(f"📝 committed dataset to subtensor chain")
            no_bug = True
            traceback.print_exc()
        except BaseException as e:
            traceback.print_exc()
            bt.logging.error(f"Error while committing to subtensor chain: {e}, retrying now...")
            time.sleep(5)
    # Push dataset after commit
    hf_dataset.push_to_hub(dataset_name, private=False, token=hf_token)
    print(f"Dataset {dataset_name} has been successfully uploaded to the Hugging Face Hub.")
    return url

# Example usage
# create_hf_dataset_from_sqlite("path/to/your/database.db", "your_table_name", "your_dataset_name", "Description of your dataset")
