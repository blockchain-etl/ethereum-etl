import os
from datetime import date

import pytest
from web3 import HTTPProvider, Web3

from ethereumetl.service.eth_service import EthService
from ethereumetl.service.graph_operations import OutOfBoundsError

skip_long_tests = os.environ.get('ETHEREUM_ETL_RUN_LONG_TESTS', None) != '1'
skip = pytest.mark.skipif(skip_long_tests, reason='Long running tests')

web3 = Web3(HTTPProvider('https://mainnet.infura.io/'))
eth_service = EthService(web3)


@skip
def test_get_block_range_for_date():
    blocks = eth_service.get_block_range_for_date(date(2015, 7, 30))
    assert blocks == (0, 6911)

    blocks = eth_service.get_block_range_for_date(date(2015, 7, 31))
    assert blocks == (6912, 13774)

    blocks = eth_service.get_block_range_for_date(date(2017, 1, 1))
    assert blocks == (2912407, 2918517)

    blocks = eth_service.get_block_range_for_date(date(2017, 1, 2))
    assert blocks == (2918518, 2924575)

    blocks = eth_service.get_block_range_for_date(date(2018, 6, 10))
    assert blocks == (5761663, 5767303)

    with pytest.raises(OutOfBoundsError):
        eth_service.get_block_range_for_date(date(2015, 7, 29))

    with pytest.raises(OutOfBoundsError):
        eth_service.get_block_range_for_date(date(2030, 1, 1))


@skip
def test_get_block_range_for_timestamps():
    blocks = eth_service.get_block_range_for_timestamps(1438270128, 1438270128)
    assert blocks == (10, 10)

    blocks = eth_service.get_block_range_for_timestamps(1438270128, 1438270129)
    assert blocks == (10, 10)

    with pytest.raises(ValueError):
        eth_service.get_block_range_for_timestamps(1438270129, 1438270131)
