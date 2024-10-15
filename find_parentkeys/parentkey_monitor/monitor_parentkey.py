import os
import sys
import logging
import json
import django
import bittensor as bt
from find_parentkeys.utils.get_parentkey import RPCRequest
from typing import List, Tuple, Dict
from find_parentkeys.database_manage.db_manage import DataBaseManager

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bt_childkey_monitor.settings')
django.setup()

from validators.models import Validators

logging.basicConfig(level=logging.INFO)

class ParentkeyMonitor:
    
    def __init__(self) -> None:
        pass
    
    def get_subnet_uids(self, subtensor) -> List[int]:
        try:
            subnet_uids = subtensor.get_subnets()
            logging.info(f"Subnet UIDs: {subnet_uids}")
            return subnet_uids
        except Exception as e:
            logging.error(f"Error retrieving subnet UIDs: {e}")
            return []

    def get_subnet_validators(self, netuid: int, subtensor) -> List[Validators]:
        big_validators: Dict[Validators, Validators] = {}
        try:
            metagraph = subtensor.metagraph(netuid)
            neuron_uids = metagraph.uids.tolist()
            stakes = metagraph.S.tolist()
            hotkeys = metagraph.hotkeys
            coldkeys = metagraph.coldkeys
            for i in range(len(neuron_uids)):
                if stakes[i] > 1000:
                    validator = Validators(coldkey=coldkeys[i], hotkey=hotkeys[i], stake=stakes[i])
                    parentkey_netuids = validator.get_parentkey_netuids()  # Deserialize JSON to list
                    parentkey_netuids.append(netuid)
                    validator.parentkey_netuids = json.dumps(parentkey_netuids)  # Serialize back to JSON
                    big_validators[validator] = validator
        except Exception as e:
            logging.error(f"Error retrieving validators for subnet {netuid}: {e}")
        return list(big_validators.values())

    def get_all_validators_subnets(self, subtensor) -> Tuple[List[Validators], List[int]]:
        all_validators: Dict[Validators, Validators] = {}
        subnet_net_uids = self.get_subnet_uids(subtensor)
        subnet_net_uids.remove(0)  # Remove the root subnet
        subnet_net_uids = [39, 23]
        if not subnet_net_uids:
            return [], []
        for netuid in subnet_net_uids:
            subnet_validators = self.get_subnet_validators(netuid, subtensor)
            for validator in subnet_validators:
                if validator not in all_validators:
                    all_validators[validator] = validator
        logging.info("Created entries for all parent validators")
        return list(all_validators.values()), subnet_net_uids

def monitor_parentkeys(config):
        
    ParentMonitor = ParentkeyMonitor()


    FullProportion = config.get("FULL_PROPORTION")
    SubtensorModule = config.get("SubtensorModule")
    ParentKeys = config.get("ParentKeys")
    chain_endpoint = config.get("CHAIN_ENDPOINT")
    
    subtensor = bt.Subtensor(network=chain_endpoint)
    SDKCall = RPCRequest(chain_endpoint, SubtensorModule, ParentKeys, FullProportion)
    db_path = config.get("DATABASE_DIR") + '/db.sqlite3'
    
    DBManager = DataBaseManager(db_path)
    
    DBManager.delete_database_file()

    DBManager.migrate_db()
    
    all_validators, subnet_uids = ParentMonitor.get_all_validators_subnets(subtensor)

    for validator in all_validators:     
        logging.info(f"Validator: {validator.__dict__}")
        parent_keys = SDKCall.get_parent_keys(validator.hotkey, subnet_uids)

        for parent_key in parent_keys:
            validator.add_parentkeys(parent_key['hotkey'], parent_key['proportion'], parent_key['net_uid'])
            
            parent_validator = next((v for v in all_validators if v.hotkey == parent_key['hotkey']), None)

            if parent_validator is None:
                # If parent validator does not exist, create a new Validator instance
                parent_validator = Validators(coldkey='', hotkey=parent_key['hotkey'], stake=0)
                all_validators.append(parent_validator)

            # Add the current validator's hotkey as a childkey to the parent validator
            parent_validator.add_childkeys(validator.hotkey, parent_key['proportion'], parent_key['net_uid'])

    for validator in all_validators:
        logging.info(f"Updating or creating validator: {validator.__dict__}")
        try:
            Validators.objects.update_or_create(
                hotkey=validator.hotkey,
                defaults={
                    'coldkey': validator.coldkey,
                    'stake': validator.stake,
                    'parentkeys': json.dumps(validator.parentkeys),  # Serialize to JSON
                    'childkeys': json.dumps(validator.childkeys)   # Serialize to JSON
                }
            )
        except Exception as e:
            logging.error(f"Error updating or creating validator {validator.hotkey}: {e}")

    DBManager.create_validator_childkey_tables(all_validators)
