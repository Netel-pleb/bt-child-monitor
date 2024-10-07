import bittensor as bt
from dotenv import load_dotenv
import os

load_dotenv()
from substrateinterface import SubstrateInterface

# substrate = SubstrateInterface(url="ws://127.0.0.1:9945")
# netuid = 1
# result = substrate.query('SubtensorModule', 'SubnetworkN', [netuid])
# print(result.value)
chain_endpoint = os.getenv("CHAIN_ENDPOINT")
subtensor = bt.Subtensor(network=chain_endpoint)
# subnet_uids = subtensor.get_all_subnet_netuids()
# print(subnet_uids)
uids = subtensor.get_subnets()
print(uids)
# metagraph = subtensor.metagraph(5)
# print(metagraph.S[1])
# print(metagraph.S[4])
# print(metagraph.uids)
# stakes = metagraph.S.tolist()
# print(stakes)
# sorted_stakes = sorted(stakes, reverse=True)
# print(sorted_stakes)
# miners_uids = metagraph.uids.tolist()
# print(miners_uids)
# print(metagraph)
# hotkey = metagraph.hotkeys[0]
# hotkeys = metagraph.hotkeys
# print(hotkeys)
# print(hotkey)