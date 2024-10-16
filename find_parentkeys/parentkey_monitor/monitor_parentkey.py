import os
import logging
import django
from typing import List, Tuple, Dict
import bittensor as bt
from find_parentkeys.utils.get_parentkey import RPCRequest
from find_parentkeys.database_manage.db_manage import DataBaseManager

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bt_childkey_monitor.settings')
django.setup()

from validators.models import HotkeyModel, ChildHotkeyModel

class ParentkeyMonitor:
    """
    Monitors and manages parent keys in the blockchain network.
    """

    def __init__(self) -> None:
        """
        Initialize the ParentkeyMonitor class.
        """
        pass  
    
    def get_subnet_uids(self, subtensor) -> List[int]:
        """
        Retrieve subnet UIDs from the subtensor.

        :param subtensor: The subtensor object to interact with.
        :return: A list of subnet UIDs.
        """
        try:
            subnet_uids = subtensor.get_subnets()
            logging.info(f"Subnet UIDs: {subnet_uids}")
            return subnet_uids
        except Exception as e:
            logging.error(f"Error retrieving subnet UIDs: {e}")
            return []

    def get_subnet_validators(self, netuid: int, subtensor) -> List[HotkeyModel]:
        """
        Retrieve validators for a specific subnet.

        :param netuid: The network UID of the subnet.
        :param subtensor: The subtensor object to interact with.
        :return: A list of Validators objects.
        """
        big_validators: Dict[HotkeyModel, HotkeyModel] = {}
        try:
            metagraph = subtensor.metagraph(netuid)
            neuron_uids = metagraph.uids.tolist()
            stakes = metagraph.S.tolist()
            hotkeys = metagraph.hotkeys

            for i in range(len(neuron_uids)):
                if stakes[i] > 1000:
                    hotkey = HotkeyModel(
                        hotkey = hotkeys[i],
                    )
                    big_validators[hotkey] = hotkey
        except Exception as e:
            logging.error(f"Error retrieving validators for subnet {netuid}: {e}")
            
        return list(big_validators.values())

    def get_all_validators_subnets(self, subtensor) -> Tuple[List[HotkeyModel], List[int]]:
        """
        Retrieve all validators and their associated subnets.

        :param subtensor: The subtensor object to interact with.
        :return: A tuple containing a list of all Validators and a list of subnet UIDs.
        """
        all_validators: Dict[HotkeyModel, HotkeyModel] = {}
        subnet_net_uids = self.get_subnet_uids(subtensor)
        subnet_net_uids.remove(0)  # Remove the root subnet
        # subnet_net_uids = [1, 3]  # Example: specify subnets of interest

        for netuid in subnet_net_uids:
            subnet_validators = self.get_subnet_validators(netuid, subtensor)
            for validator in subnet_validators:
                if validator not in all_validators:
                    all_validators[validator] = validator

        logging.info("Created entries for all parent validators")
        return list(all_validators.values()), subnet_net_uids

def monitor_parentkeys(config: Dict) -> None:
    """
    Monitors parent keys and updates the database with the latest information.

    :param config: A dictionary containing configuration settings.
    """
    parent_monitor = ParentkeyMonitor()

    full_proportion = config.get("FULL_PROPORTION")
    subtensor_call_module = config.get("SUBTENSORMODULE")
    parent_keys_call_function = config.get("PARENTKEYS_FUNCTION")
    total_hotkey_stake_call_function = config.get("TOTALHOTKEYSTAKE_FUNCTION")
    chain_endpoint = config.get("CHAIN_ENDPOINT")

    subtensor = bt.Subtensor(network=chain_endpoint)

    sdk_call = RPCRequest(chain_endpoint, full_proportion)

    db_path = os.path.join(config.get("DATABASE_DIR"), 'db.sqlite3')
    db_manager = DataBaseManager(db_path)

    db_manager.delete_database_file()
    db_manager.migrate_db()

    all_validators, subnet_uids = parent_monitor.get_all_validators_subnets(subtensor)
    for validator in all_validators:
        validator.stake = sdk_call.get_stake_from_hotkey(subtensor_call_module, total_hotkey_stake_call_function, validator.hotkey)
        validator.save()
        
    for validator in all_validators:
        parent_keys = sdk_call.get_parent_keys(subtensor_call_module, parent_keys_call_function, validator.hotkey, subnet_uids)
        for parent_key in parent_keys:
            if HotkeyModel.objects.filter(hotkey=parent_key['hotkey']).exists():
                parent_validator = HotkeyModel.objects.get(hotkey=parent_key['hotkey'])
            else:
                cur_stake = sdk_call.get_stake_from_hotkey(subtensor_call_module, total_hotkey_stake_call_function, parent_key['hotkey'])
                parent_validator = HotkeyModel.objects.create(
                    hotkey=parent_key['hotkey'],
                    stake=cur_stake,
                )
            ChildHotkeyModel.objects.create(
                parent=parent_validator,
                child=validator,
                netuid=parent_key['net_uid'],
                proportion=parent_key['proportion']
            )

