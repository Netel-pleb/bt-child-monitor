import bittensor as bt
from dotenv import load_dotenv
import os
import logging
from child_monitor.utils.get_parentkey import RPCRequest
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

subtensorModule = '658faa385070e074c85bf6b568cf0555' # fex code for SubtensorModule call_module
parentKeys = 'de41ae13ae40a9d3c5fd9b3bdea86fe2' # fex code for parentkeys call_function

GetParentKeys = RPCRequest(subtensorModule, parentKeys)


# Retrieve chain endpoint from environment variables
chain_endpoint = os.getenv("CHAIN_ENDPOINT")
if not chain_endpoint:
    raise ValueError("CHAIN_ENDPOINT environment variable is not set.")

# Initialize Subtensor
subtensor = bt.Subtensor(network=chain_endpoint)

class Validator:
    def __init__(self, coldkey, hotkey, stake):
        self.coldkey = coldkey
        self.hotkey = hotkey
        self.stake = stake
        self.parentkey_netuids = []
        self.childkeys = []
        self.parentkeys = []

    def __eq__(self, other):
        return (self.coldkey == other.coldkey and
                self.hotkey == other.hotkey)

    def __hash__(self):
        return hash((self.coldkey, self.hotkey))
    
    def add_parentkeys(self, parent_hotkey, stake, net_uid):
        # Method to add a childkey dictionary to the childkeys list
        parnetkey_info = {
            'child_hotkey': parent_hotkey,
            'stake': stake,
            'net_uid': net_uid
        }
        self.parentkeys.append(parnetkey_info) 
        
    def add_childkey(self, child_hotkey, stake, net_uid):
        # Method to add a childkey dictionary to the childkeys list
        childkey_info = {
            'child_hotkey': child_hotkey,
            'stake': stake,
            'net_uid': net_uid
        }
        self.childkeys.append(childkey_info)
    
# 5F953EH5EVc9BUKYLhktAdzH1waVdgEtwyh5ygTrwCuJkwML
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
            validator.parentkey_netuids.append(netuid)
            big_validators[validator] = validator
    return list(big_validators.values())

def get_all_validators(subnet_net_uids, subtensor):
    all_validators = {}
    for netuid in subnet_net_uids:
        subnet_validators = get_subnet_validators(netuid, subtensor)
        for validator in subnet_validators:
            if validator in all_validators:
                all_validators[validator].parentkey_netuids.extend(uid for uid in validator.parentkey_netuids if uid not in all_validators[validator].parentkey_netuids)
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
    all_validators = []
    subnet_uids = get_subnet_uids(subtensor)
    subnet_uids = [1, 2]
    all_validators = get_all_validators(subnet_uids, subtensor)
    for validator in all_validators:
        logging.info(f"Validator: {validator.__dict__}")
    for validator in all_validators:
        parent_keys = GetParentKeys.get_parent_keys(validator.hotkey, validator.parentkey_netuids)
        for parent_key in parent_keys:
            validator.add_parentkeys(parent_key['hotkey'], parent_key['proportion'], parent_key['net_uid'])
            
            parent_validator = next((v for v in all_validators if v.hotkey == parent_key['hotkey']), None)

            if parent_validator is None:
                # If parent validator does not exist, create a new Validator instance
                parent_validator = Validator(coldkey='', hotkey=parent_key['hotkey'], stake=0)
                all_validators.append(parent_validator)

            # Add the current validator's hotkey as a childkey to the parent validator
            parent_validator.add_childkeys(validator.hotkey)
        
    




