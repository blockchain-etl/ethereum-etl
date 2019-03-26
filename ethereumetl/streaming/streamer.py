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


import logging
import os
import time

from ethereumetl.file_utils import smart_open
from ethereumetl.jobs.export_blocks_job import ExportBlocksJob
from ethereumetl.jobs.export_receipts_job import ExportReceiptsJob
from ethereumetl.jobs.exporters.console_item_exporter import ConsoleItemExporter
from ethereumetl.jobs.exporters.in_memory_item_exporter import InMemoryItemExporter
from ethereumetl.jobs.extract_token_transfers_job import ExtractTokenTransfersJob
from ethereumetl.logging_utils import logging_basic_config
from ethereumetl.streaming.enrich import enrich_transactions, enrich_logs, enrich_token_transfers
from web3 import Web3

logging_basic_config()


class Streamer:
    def __init__(
            self,
            batch_web3_provider,
            last_synced_block_file='last_synced_block.txt',
            lag=0,
            item_exporter=ConsoleItemExporter(),
            start_block=None,
            end_block=None,
            period_seconds=10,
            batch_size=100,
            block_batch_size=10,
            max_workers=5):
        self.batch_web3_provider = batch_web3_provider
        self.last_synced_block_file = last_synced_block_file
        self.lag = lag
        self.item_exporter = item_exporter
        self.start_block = start_block
        self.end_block = end_block
        self.period_seconds = period_seconds
        self.batch_size = batch_size
        self.block_batch_size = block_batch_size
        self.max_workers = max_workers

    def stream(self):
        if self.start_block is not None or not os.path.isfile(self.last_synced_block_file):
            init_last_synced_block_file((self.start_block or 0) - 1, self.last_synced_block_file)

        last_synced_block = read_last_synced_block(self.last_synced_block_file)

        self.item_exporter.open()

        while True and (self.end_block is None or last_synced_block < self.end_block):
            blocks_to_sync = 0

            try:
                current_block = int(Web3(self.batch_web3_provider).eth.getBlock("latest").number)
                target_block = self._calculate_target_block(current_block, last_synced_block)
                blocks_to_sync = max(target_block - last_synced_block, 0)
                logging.info('Current block {}, target block {}, last synced block {}, blocks to sync {}'.format(
                    current_block, target_block, last_synced_block, blocks_to_sync))

                if blocks_to_sync == 0:
                    logging.info('Nothing to sync. Sleeping {} seconds...'.format(self.period_seconds))
                    time.sleep(self.period_seconds)
                    continue

                self._export_all(last_synced_block + 1, target_block)

                logging.info('Writing last synced block {}'.format(target_block))
                write_last_synced_block(self.last_synced_block_file, target_block)
                last_synced_block = target_block
            except Exception as e:
                # https://stackoverflow.com/a/4992124/1580227
                logging.exception('An exception occurred while fetching block data.')

            if blocks_to_sync != self.block_batch_size and last_synced_block != self.end_block:
                logging.info('Sleeping {} seconds...'.format(self.period_seconds))
                time.sleep(self.period_seconds)

        self.item_exporter.close()

    def _calculate_target_block(self, current_block, last_synced_block):
        target_block = current_block - self.lag
        target_block = min(target_block, last_synced_block + self.block_batch_size)
        target_block = min(target_block, self.end_block) if self.end_block is not None else target_block
        return target_block

    def _export_all(self, start_block, end_block):
        # Export blocks and transactions
        blocks, transactions = self._export_blocks_and_transactions(start_block, end_block)

        # Export receipts and logs
        receipts, logs = self._export_receipts_and_logs(transactions)

        # Extract token transfers
        token_transfers = self._extract_token_transfers(logs)

        enriched_transactions = enrich_transactions(blocks, transactions, receipts)

        enriched_logs = enrich_logs(blocks, logs)

        enriched_token_transfers = enrich_token_transfers(blocks, token_transfers)

        logging.info('Publishing to PubSub')

        self.item_exporter.export_items(blocks + enriched_transactions + enriched_logs + enriched_token_transfers)

    def _export_blocks_and_transactions(self, start_block, end_block):
        blocks_and_transactions_item_exporter = InMemoryItemExporter(item_types=['block', 'transaction'])
        blocks_and_transactions_job = ExportBlocksJob(
            start_block=start_block,
            end_block=end_block,
            batch_size=self.batch_size,
            batch_web3_provider=self.batch_web3_provider,
            max_workers=self.max_workers,
            item_exporter=blocks_and_transactions_item_exporter,
            export_blocks=True,
            export_transactions=True
        )
        blocks_and_transactions_job.run()
        blocks = blocks_and_transactions_item_exporter.get_items('block')
        transactions = blocks_and_transactions_item_exporter.get_items('transaction')
        return blocks, transactions

    def _export_receipts_and_logs(self, transactions):
        receipts_and_logs_item_exporter = InMemoryItemExporter(item_types=['receipt', 'log'])
        receipts_and_logs_job = ExportReceiptsJob(
            transaction_hashes_iterable=(transaction['hash'] for transaction in transactions),
            batch_size=self.batch_size,
            batch_web3_provider=self.batch_web3_provider,
            max_workers=self.max_workers,
            item_exporter=receipts_and_logs_item_exporter,
            export_receipts=True,
            export_logs=True
        )
        receipts_and_logs_job.run()
        receipts = receipts_and_logs_item_exporter.get_items('receipt')
        logs = receipts_and_logs_item_exporter.get_items('log')
        return receipts, logs

    def _extract_token_transfers(self, logs):
        token_transfers_item_exporter = InMemoryItemExporter(item_types=['token_transfer'])
        token_transfers_job = ExtractTokenTransfersJob(
            logs_iterable=logs,
            batch_size=self.batch_size,
            max_workers=self.max_workers,
            item_exporter=token_transfers_item_exporter)
        token_transfers_job.run()
        token_transfers = token_transfers_item_exporter.get_items('token_transfer')
        return token_transfers


def write_last_synced_block(file, last_synced_block):
    with smart_open(file, 'w') as last_synced_block_file:
        return last_synced_block_file.write(str(last_synced_block) + '\n')


def init_last_synced_block_file(start_block, last_synced_block_file):
    if os.path.isfile(last_synced_block_file):
        raise ValueError(
            '{} should not exist if --start-block option is specified. '
            'Either remove the {} file or the --start-block option.'
                .format(last_synced_block_file, last_synced_block_file))
    write_last_synced_block(last_synced_block_file, start_block)


def read_last_synced_block(file):
    with smart_open(file, 'r') as last_synced_block_file:
        return int(last_synced_block_file.read())
