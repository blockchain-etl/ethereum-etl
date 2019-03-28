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


import argparse
import itertools
import logging
import os
import time
from collections import defaultdict

from google.api_core.exceptions import GoogleAPIError
from web3 import Web3
from web3.utils.threads import Timeout

from ethereumetl.file_utils import smart_open
from ethereumetl.jobs.export_blocks_job import ExportBlocksJob
from ethereumetl.jobs.export_receipts_job import ExportReceiptsJob
from ethereumetl.jobs.exporters.google_pubsub_item_exporter import GooglePubSubItemExporter
from ethereumetl.jobs.exporters.in_memory_item_exporter import InMemoryItemExporter
from ethereumetl.jobs.extract_token_transfers_job import ExtractTokenTransfersJob
from ethereumetl.logging_utils import logging_basic_config
from ethereumetl.providers.auto import get_provider_from_uri
from ethereumetl.thread_local_proxy import ThreadLocalProxy

logging_basic_config()

parser = argparse.ArgumentParser(description='')
parser.add_argument('-l', '--last-synced-block-file', default='last_synced_block.txt', type=str, help='')
parser.add_argument('--lag', default=0, type=int, help='The number of blocks to lag behind the network.')
parser.add_argument('-p', '--provider-uri', default='https://mainnet.infura.io', type=str,
                    help='The URI of the web3 provider e.g. '
                         'file://$HOME/Library/Ethereum/geth.ipc or https://mainnet.infura.io')
parser.add_argument('-t', '--topic-path', default='projects/your-project/topics/ethereum_blockchain', type=str,
                    help='Google PubSub topic path')
parser.add_argument('-s', '--start-block', default=None, type=int, help='Start block')

args = parser.parse_args()


def write_last_synced_block(file, last_synced_block):
    with smart_open(file, 'w') as last_synced_block_file:
        return last_synced_block_file.write(str(last_synced_block) + '\n')


def init_last_synced_block_file(start_block, last_synced_block_file):
    if os.path.isfile(last_synced_block_file):
        raise ValueError(
            '{} should not exist if --start-block option is specified'.format(last_synced_block_file))
    write_last_synced_block(last_synced_block_file, start_block)


if args.start_block is not None:
    init_last_synced_block_file(args.start_block, args.last_synced_block_file)


def read_last_synced_block(file):
    with smart_open(file, 'r') as last_synced_block_file:
        return int(last_synced_block_file.read())


def join(left, right, join_fields, left_fields, right_fields):
    left_join_field, right_join_field = join_fields

    def field_list_to_dict(field_list):
        result_dict = {}
        for field in field_list:
            if isinstance(field, tuple):
                result_dict[field[0]] = field[1]
            else:
                result_dict[field] = field
        return result_dict

    left_fields_as_dict = field_list_to_dict(left_fields)
    right_fields_as_dict = field_list_to_dict(right_fields)

    left_map = defaultdict(list)
    for item in left: left_map[item[left_join_field]].append(item)

    right_map = defaultdict(list)
    for item in right: right_map[item[right_join_field]].append(item)

    for key in left_map.keys():
        for left_item, right_item in itertools.product(left_map[key], right_map[key]):
            result_item = {}
            for src_field, dst_field in left_fields_as_dict.items():
                result_item[dst_field] = left_item.get(src_field)
            for src_field, dst_field in right_fields_as_dict.items():
                result_item[dst_field] = right_item.get(src_field)

            yield result_item


def enrich_transactions(blocks, transactions, receipts):
    transactions_and_receipts = join(
        transactions, receipts, ('hash', 'transaction_hash'),
        left_fields=[
            'type',
            'hash',
            'nonce',
            'transaction_index',
            'from_address',
            'to_address',
            'value',
            'gas',
            'gas_price',
            'input',
            'block_number'
        ],
        right_fields=[
            ('cumulative_gas_used', 'receipt_cumulative_gas_used'),
            ('gas_used', 'receipt_gas_used'),
            ('contract_address', 'receipt_contract_address'),
            ('root', 'receipt_root'),
            ('status', 'receipt_status')
        ])

    result = join(
        transactions_and_receipts, blocks, ('block_number', 'number'),
        [
            'type',
            'hash',
            'nonce',
            'transaction_index',
            'from_address',
            'to_address',
            'value',
            'gas',
            'gas_price',
            'input',
            'block_number'
        ],
        [
            ('timestamp', 'block_timestamp'),
            ('hash', 'block_hash'),
        ])
    return list(result)


def enrich_logs(blocks, logs):
    result = join(
        logs, blocks, ('block_number', 'number'),
        [
            'type',
            'log_index',
            'transaction_hash',
            'transaction_index',
            'address',
            'data',
            'topics',
            'block_number'
        ],
        [
            ('timestamp', 'block_timestamp'),
            ('hash', 'block_hash'),
        ])
    return list(result)


def enrich_token_transfers(blocks, token_transfers):
    result = join(
        token_transfers, blocks, ('block_number', 'number'),
        [
            'type',
            'token_address',
            'from_address',
            'to_address',
            'value',
            'transaction_hash',
            'log_index',
            'block_number'
        ],
        [
            ('timestamp', 'block_timestamp'),
            ('hash', 'block_hash'),
        ])
    return list(result)


max_batch_size = 10
sleep_seconds = 10

last_synced_block = read_last_synced_block(args.last_synced_block_file)
web3 = Web3(get_provider_from_uri(args.provider_uri))

pubsub_item_exporter = GooglePubSubItemExporter(args.topic_path)

while True:
    blocks_to_sync = 0
    try:
        current_block = int(web3.eth.getBlock("latest").number)
        target_block = current_block - args.lag
        target_block = min(target_block, last_synced_block + max_batch_size)
        blocks_to_sync = max(target_block - last_synced_block, 0)
        logging.info('Current block {}, target block {}, last synced block {}, blocks to sync {}'.format(
            current_block, target_block, last_synced_block, blocks_to_sync))

        if blocks_to_sync == 0:
            logging.info('Nothing to sync. Sleeping {} seconds...'.format(sleep_seconds))
            time.sleep(sleep_seconds)
            continue

        # Export blocks and transactions
        blocks_and_transactions_item_exporter = InMemoryItemExporter(item_types=['block', 'transaction'])
        blocks_and_transactions_job = ExportBlocksJob(
            start_block=last_synced_block + 1,
            end_block=target_block,
            batch_size=100,
            batch_web3_provider=ThreadLocalProxy(lambda: get_provider_from_uri(args.provider_uri, batch=True)),
            max_workers=5,
            item_exporter=blocks_and_transactions_item_exporter,
            export_blocks=True,
            export_transactions=True
        )
        blocks_and_transactions_job.run()

        blocks = blocks_and_transactions_item_exporter.get_items('block')
        transactions = blocks_and_transactions_item_exporter.get_items('transaction')

        # Export receipts and logs
        receipts_and_logs_item_exporter = InMemoryItemExporter(item_types=['receipt', 'log'])
        receipts_and_logs_job = ExportReceiptsJob(
            transaction_hashes_iterable=(transaction['hash'] for transaction in transactions),
            batch_size=100,
            batch_web3_provider=ThreadLocalProxy(lambda: get_provider_from_uri(args.provider_uri, batch=True)),
            max_workers=5,
            item_exporter=receipts_and_logs_item_exporter,
            export_receipts=True,
            export_logs=True
        )
        receipts_and_logs_job.run()

        receipts = receipts_and_logs_item_exporter.get_items('receipt')
        logs = receipts_and_logs_item_exporter.get_items('log')

        # Extract token transfers
        token_transfers_item_exporter = InMemoryItemExporter(item_types=['token_transfer'])
        token_transfers_job = ExtractTokenTransfersJob(
            logs_iterable=logs,
            batch_size=100,
            max_workers=5,
            item_exporter=token_transfers_item_exporter)

        token_transfers_job.run()
        token_transfers = token_transfers_item_exporter.get_items('token_transfer')

        enriched_transactions = enrich_transactions(blocks, transactions, receipts)
        if len(enriched_transactions) != len(transactions):
            raise ValueError('The number of transactions is wrong ' + str(enriched_transactions))
        enriched_logs = enrich_logs(blocks, logs)
        if len(enriched_logs) != len(logs):
            raise ValueError('The number of logs is wrong ' + str(enriched_logs))
        enriched_token_transfers = enrich_token_transfers(blocks, token_transfers)
        if len(enriched_token_transfers) != len(token_transfers):
            raise ValueError('The number of token transfers is wrong ' + str(enriched_token_transfers))

        logging.info('Publishing to PubSub')
        pubsub_item_exporter.export_items(blocks + enriched_transactions + enriched_logs + enriched_token_transfers)

        logging.info('Writing last synced block {}'.format(target_block))
        write_last_synced_block(args.last_synced_block_file, target_block)
        last_synced_block = target_block
    except (GoogleAPIError, RuntimeError, OSError, IOError, TypeError, NameError, ValueError, Timeout) as e:
        logging.info('An exception occurred {}'.format(repr(e)))

    if blocks_to_sync != max_batch_size:
        logging.info('Sleeping {} seconds...'.format(sleep_seconds))
        time.sleep(sleep_seconds)
