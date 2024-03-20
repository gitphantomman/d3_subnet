from apify_client import ApifyClient

# Initialize the ApifyClient with your API token
client = ApifyClient("apify_api_QKGvP6x0znUYee9DEY2ycgFzMzNykh30fbqc")

# Prepare the Actor input
run_input = {
    "searchMode": "live",
    "maxTweets": 200,
    "maxRequestRetries": 6,
    "addUserInfo": True,
    "scrapeTweetReplies": False,
    "maxTweets": 1,
    "urls": ["https://twitter.com/ChrisWilso45487/status/1768479855878774904"],
}

# Run the Actor and wait for it to finish
run = client.actor("heLL6fUofdPgRXZie").call(run_input=run_input)

# Fetch and print Actor results from the run's dataset (if there are any)
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item)