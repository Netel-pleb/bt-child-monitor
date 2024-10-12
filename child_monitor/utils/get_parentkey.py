from substrateinterface.utils.ss58 import ss58_encode, ss58_decode
from substrateinterface import Keypair
import hashlib
import websockets
import asyncio
import json
from dotenv import load_dotenv
import os

load_dotenv()

# CHAIN_ENDPOINT = os.getenv("CHAIN_ENDPOINT") 
CHAIN_ENDPOINT = "wss://entrypoint-finney.opentensor.ai:443"
hotkey = '5GKH9FPPnWSUoeeTJp19wVtd84XqFW4pyK2ijV2GsFbhTrP1'
net_uids = [38, 39, 40]
fullProportion = 18446744073709551615

def convert_hex_to_ss58(hex_string: str, ss58_format: int = 42) -> str:
    # Extract the first 64 characters (32 bytes) for the public key
    public_key_hex = hex_string[-64:]
    
    # Convert hex string to bytes
    public_key = bytes.fromhex(public_key_hex)
    
    # Check if the public key is 32 bytes long
    if len(public_key) != 32:
        raise ValueError('Public key should be 32 bytes long')
    
    # Convert to SS58 address with specified ss58_format
    keypair = Keypair(public_key=public_key, ss58_format=ss58_format)
    return keypair.ss58_address

def convert_ss58_to_hex(ss58_address):
    # Decode SS58 address to bytes
    address_str = ss58_decode(ss58_address)
    
    address_bytes = bytes(address_str, 'utf-8')
    
    # Convert bytes to hex string and add '0x' prefix
    hex_address = '0x' + address_bytes.hex()
    
    return hex_address

def ss58_to_blake2_128concat(ss58_address: str) -> bytes:
    # Decode the SS58 address to get the raw account ID
    keypair = Keypair(ss58_address=ss58_address)
    account_id = keypair.public_key

    # Create a Blake2b hash object with a digest size of 16 bytes (128 bits)
    blake2b_hash = hashlib.blake2b(account_id, digest_size=16)
    # Get the digest
    hash_digest = blake2b_hash.digest()
    # Concatenate the hash with the original account ID
    result = hash_digest + account_id
    return result

def decimal_to_hex(decimal_num):
    """
    Convert a decimal number to a hexadecimal string.
    
    :param decimal_num: Decimal number (e.g., 612345678901234567)
    :return: Hexadecimal string
    """
    return hex(decimal_num)[2:] + '00'  # Remove the '0x' prefix

module = '658faa385070e074c85bf6b568cf0555'
method = 'de41ae13ae40a9d3c5fd9b3bdea86fe2'
blake2_128concat = ss58_to_blake2_128concat(hotkey).hex()
call_params = []
for net_uid in net_uids:
    net_uid_hex = decimal_to_hex(net_uid)
    call_hex = '0x' + module + method + blake2_128concat + net_uid_hex
    call_params.append(call_hex)
    
print(call_params)

# def call_parse(call_result):



# 0x658faa385070e074c85bf6b568cf0555de41ae13ae40a9d3c5fd9b3bdea86fe2f45a4ebe3c627b9ecc18af4978916660bc0e6b701243978c1fe73d721c7b157943a713fca9f3c88cad7a9f7799bc6b262700
# 0x658faa385070e074c85bf6b568cf0555de41ae13ae40a9d3c5fd9b3bdea86fe2f45a4ebe3c627b9ecc18af4978916660bc0e6b701243978c1fe73d721c7b157943a713fca9f3c88cad7a9f7799bc6b262700

async def get_parent_keys():
    async with websockets.connect(
        CHAIN_ENDPOINT, ping_interval=None
    ) as ws:
        await ws.send(json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "state_subscribeStorage",
                # "params": [[f"0x658faa385070e074c85bf6b568cf055564b6168414916325e7cb4f3f47691e11{subnet_hex}00"]],
                # "params" : [["0x658faa385070e074c85bf6b568cf0555eca6b7a1fdc9f689184ecb4f359c0518"]]
                # 'params' : [['0x658faa385070e074c85bf6b568cf055536e3e82152c8758267395fe524fbbd160500']]
                'params' : [call_params]
            
            }
        ))
        ignore = await ws.recv()  # ignore the first response since it's a just a confirmation
        response = await ws.recv()
        changes = json.loads(response)["params"]["result"]["changes"]
        # print(changes)
        return changes


call_results = asyncio.run(get_parent_keys())
# result = call_parse(call_result)


def convert_hex_to_ss58(hex_string: str, ss58_format: int = 42) -> str:
    # Extract the first 64 characters (32 bytes) for the public key
    public_key_hex = hex_string[-64:]
    
    # Convert hex string to bytes
    public_key = bytes.fromhex(public_key_hex)
    
    # Check if the public key is 32 bytes long
    if len(public_key) != 32:
        raise ValueError('Public key should be 32 bytes long')
    
    # Convert to SS58 address with specified ss58_format
    keypair = Keypair(public_key=public_key, ss58_format=ss58_format)
    return keypair.ss58_address

def reverse_hex(hex_string):
    # Ensure the string is exactly 16 characters long
    if len(hex_string) != 16:
        raise ValueError("Input must be a 16-character hexadecimal string.")
    
    # Split into pairs and reverse
    reversed_hex = ''.join(reversed([hex_string[i:i+2] for i in range(0, len(hex_string), 2)]))
    
    return '0x' + reversed_hex

print("results")
print(call_results)

# results = '0x0c0000000000000080befb4b2b719c0dc08273b9293fa8166180fe3c0e6e0fc9f4cb224f429dc8163cffffffffffffffff8cd280d43e4cf6501ae3b425583975ff63ce4d7470cf518074b5903ff375600e003433333333333344f7a87e1b1de487eaf9e10413f485855444a46148bfe32cf6b225fdc610a03b'

def hex_to_decimal(hex_str):
    """
    Convert a hexadecimal string to a decimal number.
    
    :param hex_str: Hexadecimal string (e.g., '0088eb51b81e85ab')
    :return: Decimal number
    """
    return int(hex_str, 16)



def get_num_results(results):
    num_results = hex_to_decimal(results[:4])
    return int(num_results / 4)


parent_keys = []
answer = {}
for result_cur, net_uid in zip(call_results, net_uids):
    result = result_cur[1]
    num_result = get_num_results(result)
    print(num_result)
    result_hexs = []
    for i in range(4, len(result), 80):
        result_hexs.append(result[i:i+80])
    print(result_hexs)    
    for result_hex in result_hexs:
        parent_hotkey = convert_hex_to_ss58(result_hex)
        parent_proportion_demical = hex_to_decimal(reverse_hex(result_hex[:16]))
        parent_proporton = parent_proportion_demical / fullProportion
        parent_keys.append({'hotkey': parent_hotkey, 'proportion': parent_proporton})
    for parent_key in parent_keys:
        answer[parent_key['hotkey']].append('child_hotkey' : hotkey, 'proportion' : parent_key['proportion'], 'net_uid' : net_uid)
print(answer)
# print(parent_keys)
