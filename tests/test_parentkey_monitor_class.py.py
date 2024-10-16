import pytest
from unittest.mock import patch, MagicMock
from find_parentkeys.parentkey_monitor.monitor_parentkey import ParentkeyMonitor

@pytest.fixture
def config():
    return {
        "FULL_PROPORTION": 18446744073709551615,
        "SUBTENSORMODULE": '658faa385070e074c85bf6b568cf0555',
        "PARENTKEYS_FUNCTION": 'de41ae13ae40a9d3c5fd9b3bdea86fe2',
        "TOTALHOTKEYSTAKE_FUNCTION": '7b4e834c482cd6f103e108dacad0ab65',
        "CHAIN_ENDPOINT": "wss://entrypoint-finney.opentensor.ai:443",
        "DATABASE_DIR": "db"
    }

@pytest.fixture
def monitor(config):
    return ParentkeyMonitor(config)

@patch('find_parentkeys.parentkey_monitor.monitor_parentkey.bt.Subtensor')
@patch('find_parentkeys.parentkey_monitor.monitor_parentkey.RPCRequest')
@patch('find_parentkeys.parentkey_monitor.monitor_parentkey.DataBaseManager')
def test_get_subnet_uids(mock_db_manager, mock_rpc_request, mock_subtensor, monitor):
    mock_subtensor.get_subnets.return_value = [1, 2, 3]
    uids = monitor.get_subnet_uids(mock_subtensor)
    assert uids == [1, 2, 3]

@patch('find_parentkeys.parentkey_monitor.monitor_parentkey.bt.Subtensor')
@patch('find_parentkeys.parentkey_monitor.monitor_parentkey.RPCRequest')
@patch('find_parentkeys.parentkey_monitor.monitor_parentkey.DataBaseManager')
def test_get_subnet_validators(mock_db_manager, mock_rpc_request, mock_subtensor, monitor):
    mock_metagraph = MagicMock()
    mock_metagraph.uids.tolist.return_value = [100, 200, 300]
    mock_metagraph.S.tolist.return_value = [1500, 500, 2000]
    mock_metagraph.hotkeys = ['hotkey1', 'hotkey2', 'hotkey3']
    mock_subtensor.metagraph.return_value = mock_metagraph

    validators = monitor.get_subnet_validators(1, mock_subtensor)
    assert len(validators) == 2
    assert validators[0].hotkey == 'hotkey1'
    assert validators[1].hotkey == 'hotkey3'

@patch('find_parentkeys.parentkey_monitor.monitor_parentkey.bt.Subtensor')
@patch('find_parentkeys.parentkey_monitor.monitor_parentkey.RPCRequest')
@patch('find_parentkeys.parentkey_monitor.monitor_parentkey.DataBaseManager')
def test_monitor_parentkeys(mock_db_manager, mock_rpc_request, mock_subtensor, monitor):
    mock_db_manager_instance = mock_db_manager.return_value
    mock_db_manager_instance.delete_database_file.return_value = None
    mock_db_manager_instance.migrate_db.return_value = None

    mock_rpc_request_instance = mock_rpc_request.return_value
    mock_rpc_request_instance.get_stake_from_hotkey.return_value = 1000
    mock_rpc_request_instance.get_parent_keys.return_value = [{'hotkey': 'parent_hotkey', 'net_uid': 1, 'proportion': 0.5}]

    monitor.monitor_parentkeys()

@patch('find_parentkeys.parentkey_monitor.monitor_parentkey.bt.Subtensor')
@patch('find_parentkeys.parentkey_monitor.monitor_parentkey.RPCRequest')
@patch('find_parentkeys.parentkey_monitor.monitor_parentkey.DataBaseManager')
def test_get_current_stake(mock_db_manager, mock_rpc_request, mock_subtensor, monitor):
    mock_rpc_request_instance = mock_rpc_request.return_value
    mock_rpc_request_instance.get_stake_from_hotkey.return_value = 1000.0
    stake = monitor._get_current_stake('hotkey1')
    assert stake == 1000.0

@patch('find_parentkeys.parentkey_monitor.monitor_parentkey.bt.Subtensor')
@patch('find_parentkeys.parentkey_monitor.monitor_parentkey.RPCRequest')
@patch('find_parentkeys.parentkey_monitor.monitor_parentkey.DataBaseManager')
def test_get_subnet_uids_error(mock_db_manager, mock_rpc_request, mock_subtensor, monitor):
    mock_subtensor.get_subnets.side_effect = Exception("Error")
    uids = monitor.get_subnet_uids(mock_subtensor)
    assert uids == []

@patch('find_parentkeys.parentkey_monitor.monitor_parentkey.bt.Subtensor')
@patch('find_parentkeys.parentkey_monitor.monitor_parentkey.RPCRequest')
@patch('find_parentkeys.parentkey_monitor.monitor_parentkey.DataBaseManager')
def test_get_subnet_validators_no_stake(mock_db_manager, mock_rpc_request, mock_subtensor, monitor):
    mock_metagraph = MagicMock()
    mock_metagraph.uids.tolist.return_value = [100, 200, 300]
    mock_metagraph.S.tolist.return_value = [500, 500, 500]  # Below threshold
    mock_metagraph.hotkeys = ['hotkey1', 'hotkey2', 'hotkey3']
    mock_subtensor.metagraph.return_value = mock_metagraph

    validators = monitor.get_subnet_validators(1, mock_subtensor)
    assert len(validators) == 0

@patch('find_parentkeys.parentkey_monitor.monitor_parentkey.bt.Subtensor')
@patch('find_parentkeys.parentkey_monitor.monitor_parentkey.RPCRequest')
@patch('find_parentkeys.parentkey_monitor.monitor_parentkey.DataBaseManager')
def test_monitor_parentkeys_no_validators(mock_db_manager, mock_rpc_request, mock_subtensor, monitor):
    mock_db_manager_instance = mock_db_manager.return_value
    mock_db_manager_instance.delete_database_file.return_value = None
    mock_db_manager_instance.migrate_db.return_value = None

    mock_rpc_request_instance = mock_rpc_request.return_value
    mock_rpc_request_instance.get_stake_from_hotkey.return_value = 1000
    mock_rpc_request_instance.get_parent_keys.return_value = []

    with patch.object(monitor, 'get_all_validators_subnets', return_value=([], [])):
        monitor.monitor_parentkeys()

