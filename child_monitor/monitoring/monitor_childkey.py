import bittensor as bt
from dotenv import load_dotenv
import os
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Retrieve chain endpoint from environment variables
chain_endpoint = os.getenv("CHAIN_ENDPOINT")
if not chain_endpoint:
    raise ValueError("CHAIN_ENDPOINT environment variable is not set.")

# Initialize Subtensor
subtensor = bt.Subtensor(network=chain_endpoint)

class Validator:
    def __init__(self, coldkey, hotkey, stake, net_uid):
        self.coldkey = coldkey
        self.hotkey = hotkey
        self.stake = stake
        self.net_uid = net_uid

    def __eq__(self, other):
        return (self.coldkey == other.coldkey and
                self.hotkey == other.hotkey and
                self.stake == other.stake and
                self.net_uid == other.net_uid)

    def __hash__(self):
        return hash((self.coldkey, self.hotkey, self.stake, self.net_uid))

def get_subnet_validators(netuid, subtensor):
    try:
        big_validators = set()
        metagraph = subtensor.metagraph(netuid)
        neuron_uids = metagraph.uids.tolist()
        stakes = metagraph.S.tolist()
        hotkeys = metagraph.hotkeys
        coldkeys = metagraph.coldkeys
        for i in range(len(neuron_uids)):
            if stakes[i] > 1000:
                big_validators.add(Validator(coldkeys[i], hotkeys[i], stakes[i], netuid))
        return big_validators
    except Exception as e:
        logging.error(f"Error retrieving validators for netuid {netuid}: {e}")
        return set()

def get_subnet_uids(subtensor):
    try:
        subnet_uids = subtensor.get_subnets()
        logging.info(f"Subnet UIDs: {subnet_uids}")
        return subnet_uids
    except Exception as e:
        logging.error(f"Error retrieving subnet UIDs: {e}")
        return []

if __name__ == "__main__":
    all_validators = set()
    subnet_uids = get_subnet_uids(subtensor)
    for subnet_uid in subnet_uids:
        all_validators.update(get_subnet_validators(subnet_uid, subtensor))
    logging.info(f"All validators: {all_validators}")
    for validator in all_validators:
        logging.info(f"Validator: {validator.__dict__}")
