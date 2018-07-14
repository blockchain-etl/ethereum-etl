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
    start_block, end_block = eth_service.get_block_range_for_date(date(2017, 1, 1))
    assert start_block == 2912407
    assert end_block == 2918517
