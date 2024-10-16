import os
import time
import argparse
import yaml
import logging
from dotenv import load_dotenv
from find_parentkeys.parentkey_monitor.monitor_parentkey import ParentkeyMonitor
from find_parentkeys.utils.sentry import init_sentry

load_dotenv()
sentry_dsn = os.getenv("SENTRY_DSN")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %Z'
)

def create_db_directory(db_path: str) -> None:
    """Create a database directory if it doesn't exist."""
    if not os.path.exists(db_path):
        os.makedirs(db_path)
        logging.info(f"Created directory: {db_path}")
    else:
        logging.info(f"Directory already exists: {db_path}")

def run_bot(timestamp: int, config: dict) -> None:
    """Run the parent key monitoring function continuously."""
    parent_monitor = ParentkeyMonitor(config)
    while True:
        parent_monitor.monitor_parentkeys()  # Monitor parent keys
        logging.info(f"monitor_Childkeys finished, sleeping for {timestamp} seconds")
        time.sleep(timestamp)  # Delay for specified time

def main():
    """Main entry point for the bot."""
    parser = argparse.ArgumentParser(description="Initialize and run the bot.")
    parser.add_argument("config_file", nargs='?', default='config.yaml', help="Path to the YAML configuration file.")
    parser.add_argument("--interval", type=int, default=3600, help="Delay between runs in seconds.")
    args = parser.parse_args()

    init_sentry(sentry_dsn)

    with open(args.config_file, "r") as f:
        config = yaml.safe_load(f)

    db_dir = config.get("DATABASE_DIR")
    create_db_directory(db_dir)  # Create a database directory

    run_bot(args.interval, config)

if __name__ == '__main__':
    main()
