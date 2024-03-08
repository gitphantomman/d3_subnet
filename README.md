<div align="center">

# **Bittensor Subnet Template** <!-- omit in toc -->
[![Discord Chat](https://img.shields.io/discord/308323056592486420.svg)](https://discord.gg/bittensor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 

---

## The Incentivized Internet <!-- omit in toc -->

[Discord](https://discord.gg/bittensor) • [Network](https://taostats.io/) • [Research](https://bittensor.com/whitepaper)
</div>


## Installation.

### Clone the repository from github

```bash
git clone https://github.com/gitphantomman/scraping_subnet_new.git
cd scraping_subnet_new
```

### Install python virtual environment

```bash
python3 -m venv my-env
. my-env/bin/activate
```

### Install dependancies

```bash
python3 -m pip install -e .
python3 -m pip install -r requirements.txt
```

### Register hotkey to subnet

- Please reference [Register guide](./docs/register.md).
- Check if you're registered to subnet using `btcli w overview --subtensor.network test --wallet.name miner`.
- You can check the metagraph using `btcli subnets metagraph --subtensor.network test --netuid 18`.

## Running Miner

```bash
python neurons/miner.py --subtensor.network test --netuid 18 --wallet.name test_miner1 --wallet.hotkey default --axon.port 8091 --logging.debug
```

- Extended Running CLI
    ```bash
    python neurons/miner.py --subtensor.network test --netuid 18 --wallet.name test_miner1 --wallet.hotkey default --axon.port 8091 --logging.debug --num_blocks_for_commit 7 --scrape_interval 5 --db_directory data/
    ```

## Running validator

```bash
python neurons/validator.py --subtensor.network test --netuid 18 --wallet.name test_validator --wallet.hotkey default --axon.port 8092 --logging.debug
```


## License
This repository is licensed under the MIT License.
```text
# The MIT License (MIT)
# Copyright © 2023 Yuma Rao

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
```
