import logging
import os
import json
from django.core.management import call_command
import bittensor as bt
import django
from typing import List

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bt_childkey_monitor.settings')
django.setup()

from validators.models import ValidatorChildKeyInfo, Validators

class DataBaseManager:
    
    def __init__(self, db_path) -> None:
        self.db_path = db_path
    
    def delete_database_file(self) -> None:
        # base_dir = os.path.dirname(os.path.abspath(__file__))
        # self.db_path = os.path.join(base_dir, 'db', 'db.sqlite3')
        logging.info(f"Deleting database file: {self.db_path}")
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            logging.info("Deleted database file")
        else:
            logging.info("Database file does not exist, skipping deletion")

    def migrate_db(self) -> None:
        try:
            call_command('makemigrations')
            call_command('migrate')
            logging.info("Database migrated successfully.")
        except Exception as e:
            logging.error(f"Error migrating database: {e}")

    def create_validator_childkey_tables(self, parent_validators: List[Validators]) -> None:
        for validator in parent_validators:
            try:
                parent_coldkey = validator.coldkey
                parent_stake = validator.stake
                childkeys_info = validator.childkeys if isinstance(validator.childkeys, list) else json.loads(validator.childkeys)
                if not childkeys_info:
                    continue
                for child_info in childkeys_info:
                    ValidatorChildKeyInfo.objects.create(
                        parent_hotkey=validator,
                        parent_coldkey=parent_coldkey,
                        parent_stake=parent_stake,
                        child_hotkey=child_info['child_hotkey'],
                        stake_proportion=child_info['proportion'],
                        subnet_uid=child_info['net_uid']
                    )
                    logging.info(f"Created child key info for {validator.hotkey}: {child_info['child_hotkey']}")
            except Exception as e:
                logging.error(f"Error creating child key info for {validator.hotkey}: {e}")
