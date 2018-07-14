import os

import pytest
from dateutil.parser import parse
from web3 import HTTPProvider, Web3

from ethereumetl.service.eth_service import EthService
from ethereumetl.service.graph_operations import OutOfBoundsError

run_slow_tests = os.environ.get('ETHEREUM_ETL_RUN_SLOW_TESTS', None) == '1'
skip_slow_tests = pytest.mark.skipif(not run_slow_tests, reason='Slow running tests')


@skip_slow_tests
@pytest.mark.parametrize("date,expected_start_block,expected_end_block", [
    ('2015-07-30', 0, 6911),
    ('2015-07-31', 6912, 13774),
    ('2017-01-01', 2912407, 2918517),
    ('2017-01-02', 2918518, 2924575),
    ('2018-06-10', 5761663, 5767303)
])
def test_get_block_range_for_date(date, expected_start_block, expected_end_block):
    eth_service = get_new_eth_service()
    parsed_date = parse(date)
    blocks = eth_service.get_block_range_for_date(parsed_date)
    assert blocks == (expected_start_block, expected_end_block)


@skip_slow_tests
@pytest.mark.parametrize("date", [
    '2015-07-29',
    '2030-01-01'
])
def test_get_block_range_for_date_fail(date):
    eth_service = get_new_eth_service()
    parsed_date = parse(date)
    with pytest.raises(OutOfBoundsError):
        eth_service.get_block_range_for_date(parsed_date)


@skip_slow_tests
@pytest.mark.parametrize("start_timestamp,end_timestamp,expected_start_block,expected_end_block", [
    (1438270128, 1438270128, 10, 10),
    (1438270128, 1438270129, 10, 10)
])
def test_get_block_range_for_timestamps(start_timestamp, end_timestamp, expected_start_block, expected_end_block):
    eth_service = get_new_eth_service()
    blocks = eth_service.get_block_range_for_timestamps(start_timestamp, end_timestamp)
    assert blocks == (expected_start_block, expected_end_block)


@skip_slow_tests
@pytest.mark.parametrize("start_timestamp,end_timestamp", [
    (1438270129, 1438270131)
])
def test_get_block_range_for_timestamps_fail(start_timestamp, end_timestamp):
    eth_service = get_new_eth_service()
    with pytest.raises(ValueError):
        eth_service.get_block_range_for_timestamps(start_timestamp, end_timestamp)


def get_new_eth_service():
    web3 = Web3(HTTPProvider('https://mainnet.infura.io/'))
    return EthService(web3)
