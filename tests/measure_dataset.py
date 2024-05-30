from datasets import load_dataset
from transformers import AutoTokenizer

# Load the dataset
dataset = load_dataset('bittensor-dataset/twitter-text-dataset', split='train')
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

def count_tokens(text, max_length = 512):
    tokens = tokenizer.tokenize(text, truncation=True, max_length=max_length)
    return len(tokens)

total_tokens = 0
for example in dataset:
    total_tokens += count_tokens(example['tweet_content'])

print(f"Total number of tokens: {total_tokens}")