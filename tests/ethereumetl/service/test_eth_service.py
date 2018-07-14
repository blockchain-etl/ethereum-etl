import os
from datetime import date

import pytest
from web3 import HTTPProvider, Web3

from ethereumetl.service.eth_service import EthService

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


@skip
@pytest.mark.xfail
def test_get_block_range_for_date_fail_too_early():
    eth_service.get_block_range_for_date(date(2015, 7, 29))


@skip
@pytest.mark.xfail
def test_get_block_range_for_date_fail_too_late():
    eth_service.get_block_range_for_date(date(2030, 1, 1))
