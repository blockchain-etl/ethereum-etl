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
import logging
import time

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

args = parser.parse_args()


def read_last_synced_block(file):
    with smart_open(file, 'r') as last_synced_block_file:
        return int(last_synced_block_file.read())


def write_last_synced_block(file, last_synced_block):
    with smart_open(file, 'w') as last_synced_block_file:
        return last_synced_block_file.write(str(last_synced_block) + '\n')


max_batch_size = 10

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
            logging.info('Nothing to sync. Sleeping...')
            time.sleep(10)
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

        logging.info('Publishing to PubSub')
        pubsub_item_exporter.export_items(blocks + transactions + receipts + logs + token_transfers)

        logging.info('Writing last synced block {}'.format(target_block))
        write_last_synced_block(args.last_synced_block_file, target_block)
        last_synced_block = target_block
    except (GoogleAPIError, RuntimeError, OSError, IOError, TypeError, NameError, ValueError, Timeout) as e:
        logging.info('An exception occurred {}'.format(repr(e)))

    if blocks_to_sync != max_batch_size:
        time.sleep(10)
