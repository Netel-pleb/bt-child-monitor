import bittensor as bt
from dotenv import load_dotenv
import os
import logging
# from child_monitor.utils.get_parentkey import get_parent_keys

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Retrieve chain endpoint from environment variables
chain_endpoint = os.getenv("CHAIN_ENDPOINT")
if not chain_endpoint:
    raise ValueError("CHAIN_ENDPOINT environment variable is not set.")

# Initialize Subtensor
subtensor = bt.Subtensor(network=chain_endpoint)

# class Validator:
#     def __init__(self, coldkey, hotkey, stake):
#         self.coldkey = coldkey
#         self.hotkey = hotkey
#         self.stake = stake
#         self.net_uids = []

#     def __eq__(self, other):
#         return (self.coldkey == other.coldkey and
#                 self.hotkey == other.hotkey and
#                 self.stake == other.stake)

#     def __hash__(self):
#         return hash((self.coldkey, self.hotkey, self.stake))

# def get_subnet_validators(netuid, subtensor):
#     try:
#         big_validators = set()
#         metagraph = subtensor.metagraph(netuid)
#         neuron_uids = metagraph.uids.tolist()
#         stakes = metagraph.S.tolist()
#         hotkeys = metagraph.hotkeys
#         coldkeys = metagraph.coldkeys
#         for i in range(len(neuron_uids)):
#             if stakes[i] > 1000:
#                 big_validators.add(Validator(coldkeys[i], hotkeys[i], stakes[i], netuid))
#         return big_validators
#     except Exception as e:
#         logging.error(f"Error retrieving validators for netuid {netuid}: {e}")
#         return set()

class Validator:
    def __init__(self, coldkey, hotkey, stake):
        self.coldkey = coldkey
        self.hotkey = hotkey
        self.stake = stake
        self.net_uids = []

    def __eq__(self, other):
        return (self.coldkey == other.coldkey and
                self.hotkey == other.hotkey and
                self.stake == other.stake)

    def __hash__(self):
        return hash((self.coldkey, self.hotkey, self.stake))

def get_subnet_validators(netuid, subtensor):
    big_validators = {}
    metagraph = subtensor.metagraph(netuid)
    neuron_uids = metagraph.uids.tolist()
    stakes = metagraph.S.tolist()
    hotkeys = metagraph.hotkeys
    coldkeys = metagraph.coldkeys
    for i in range(len(neuron_uids)):
        if stakes[i] > 1000:
            validator = Validator(coldkeys[i], hotkeys[i], stakes[i])
            if validator in big_validators:
                big_validators[validator].net_uids.append(netuid)
            else:
                validator.net_uids.append(netuid)
                big_validators[validator] = validator
    return list(big_validators.values())

def get_all_validators(subnet_net_uids, subtensor):
    all_validators = {}
    for netuid in subnet_net_uids:
        subnet_validators = get_subnet_validators(netuid, subtensor)
        for validator in subnet_validators:
            if validator in all_validators:
                all_validators[validator].net_uids.extend(validator.net_uids)
            else:
                all_validators[validator] = validator
    return list(all_validators.values())

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
    subnet_uids = [1, 2]
    for subnet_uid in subnet_uids:
        all_validators.update(get_subnet_validators(subnet_uid, subtensor))
    # for validator in all_validators:
        # validators_info = get_parent_keys(validator.hotkey, validator.net_uids)
        
    logging.info(f"All validators: {all_validators}")
    for validator in all_validators:
        logging.info(f"Validator: {validator.__dict__}")
