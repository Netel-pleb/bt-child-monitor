import bittensor as bt
from dotenv import load_dotenv
import os
from substrateinterface import SubstrateInterface

load_dotenv()

class validator:
    def __init__(self, uid, hotkeys, coldkey):
        self.uid = uid
        self.hotkeys = hotkeys
        self.coldkey = coldkey

    def __str__(self):
        return f"uid: {self.uid}, hotkeys: {self.hotkeys}, coldkeys: {self.coldkeys}, ip: {self.ip}, port: {self.port}, ip_type: {self.ip_type}"

    def __repr__(self):
        return f"uid: {self.uid}, hotkeys: {self.hotkeys}, coldkeys: {self.coldkeys}, ip: {self.ip}, port: {self.port}, ip_type: {self.ip_type}"

def get_subnet_uids():
    chain_endpoint = os.getenv("CHAIN_ENDPOINT")
    subtensor = bt.Subtensor(network=chain_endpoint)
    uids = subtensor.get_subnets()
    print(uids)
    return uids    


def monitor_childkey():
    # monitoring childkey information
    subnet_udis = get_subnet_uids()
    hotkeys, 
    