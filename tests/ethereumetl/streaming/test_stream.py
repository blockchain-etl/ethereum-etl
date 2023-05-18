# MIT License
#
# Copyright (c) 2018 Evgeny Medvedev, evge.medvedev@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os

import pytest
from ethereumetl.streaming.eth_streamer_adapter import EthStreamerAdapter
from ethereumetl.thread_local_proxy import ThreadLocalProxy

import tests.resources
from ethereumetl.enumeration.entity_type import EntityType
from blockchainetl.jobs.exporters.composite_item_exporter import CompositeItemExporter
from blockchainetl.streaming.streamer import Streamer
from tests.ethereumetl.job.helpers import get_web3_provider
from tests.helpers import compare_lines_ignore_order, read_file, skip_if_slow_tests_disabled

RESOURCE_GROUP = 'test_stream'


def read_resource(resource_group, file_name):
    return tests.resources.read_resource([RESOURCE_GROUP, resource_group], file_name)


@pytest.mark.parametrize("start_block, end_block, batch_size, resource_group, entity_types, provider_type", [
    (1755634, 1755635, 1, 'blocks_1755634_1755635', EntityType.ALL_FOR_INFURA, 'mock'),
    skip_if_slow_tests_disabled([1755634, 1755635, 1, 'blocks_1755634_1755635', EntityType.ALL_FOR_INFURA, 'infura']),
    (508110, 508110, 1, 'blocks_508110_508110', ['trace', 'contract', 'token'], 'mock'),
    (2112234, 2112234, 1, 'blocks_2112234_2112234', ['trace', 'contract', 'token'], 'mock'),
    skip_if_slow_tests_disabled([17173049, 17173050, 1, 'blocks_17173049_17173050', EntityType.ALL_FOR_INFURA, 'infura']),
])
def test_stream(tmpdir, start_block, end_block, batch_size, resource_group, entity_types, provider_type):
    try:
        os.remove('last_synced_block.txt')
    except OSError:
        pass

    blocks_output_file = str(tmpdir.join('actual_blocks.json'))
    transactions_output_file = str(tmpdir.join('actual_transactions.json'))
    logs_output_file = str(tmpdir.join('actual_logs.json'))
    token_transfers_output_file = str(tmpdir.join('actual_token_transfers.json'))
    traces_output_file = str(tmpdir.join('actual_traces.json'))
    contracts_output_file = str(tmpdir.join('actual_contracts.json'))
    tokens_output_file = str(tmpdir.join('actual_tokens.json'))

    streamer_adapter = EthStreamerAdapter(
        batch_web3_provider=ThreadLocalProxy(
            lambda: get_web3_provider(provider_type,
                                      read_resource_lambda=lambda file: read_resource(resource_group, file),
                                      batch=True)
        ),
        batch_size=batch_size,
        item_exporter=CompositeItemExporter(
            filename_mapping={
                'block': blocks_output_file,
                'transaction': transactions_output_file,
                'log': logs_output_file,
                'token_transfer': token_transfers_output_file,
                'trace': traces_output_file,
                'contract': contracts_output_file,
                'token': tokens_output_file,
            }
        ),
        entity_types=entity_types,
    )
    streamer = Streamer(
        blockchain_streamer_adapter=streamer_adapter,
        start_block=start_block,
        end_block=end_block,
        retry_errors=False
    )
    streamer.stream()

    if 'block' in entity_types:
        print('=====================')
        print(read_file(blocks_output_file))
        compare_lines_ignore_order(
            read_resource(resource_group, 'expected_blocks.json'), read_file(blocks_output_file)
        )

    if 'transaction' in entity_types:
        print('=====================')
        print(read_file(transactions_output_file))
        compare_lines_ignore_order(
            read_resource(resource_group, 'expected_transactions.json'), read_file(transactions_output_file)
        )

    if 'log' in entity_types:
        print('=====================')
        print(read_file(logs_output_file))
        compare_lines_ignore_order(
            read_resource(resource_group, 'expected_logs.json'), read_file(logs_output_file)
        )

    if 'token_transfer' in entity_types:
        print('=====================')
        print(read_file(token_transfers_output_file))
        compare_lines_ignore_order(
            read_resource(resource_group, 'expected_token_transfers.json'), read_file(token_transfers_output_file)
        )

    if 'trace' in entity_types:
        print('=====================')
        print(read_file(traces_output_file))
        compare_lines_ignore_order(
            read_resource(resource_group, 'expected_traces.json'), read_file(traces_output_file)
        )

    if 'contract' in entity_types:
        print('=====================')
        print(read_file(contracts_output_file))
        compare_lines_ignore_order(
            read_resource(resource_group, 'expected_contracts.json'), read_file(contracts_output_file)
        )

    if 'token' in entity_types:
        print('=====================')
        print(read_file(tokens_output_file))
        compare_lines_ignore_order(
            read_resource(resource_group, 'expected_tokens.json'), read_file(tokens_output_file)
        )
