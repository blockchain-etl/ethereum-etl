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

from ethereumetl.enumeration.entity_type import EntityType
from ethereumetl.file_utils import smart_open
from ethereumetl.jobs.export_blocks_job import ExportBlocksJob
from ethereumetl.jobs.export_receipts_job import ExportReceiptsJob
from ethereumetl.jobs.export_tokens_job import ExportTokensJob
from ethereumetl.jobs.export_traces_job import ExportTracesJob
from ethereumetl.jobs.exporters.console_item_exporter import ConsoleItemExporter
from ethereumetl.jobs.exporters.in_memory_item_exporter import InMemoryItemExporter
from ethereumetl.jobs.extract_contracts_job import ExtractContractsJob
from ethereumetl.jobs.extract_token_transfers_job import ExtractTokenTransfersJob
from ethereumetl.streaming.enrich import enrich_transactions, enrich_logs, enrich_token_transfers, enrich_traces, \
    enrich_contracts
from ethereumetl.thread_local_proxy import ThreadLocalProxy
from timeout_decorator import timeout_decorator
from web3 import Web3


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
            max_workers=5,
            entity_types=tuple(EntityType.ALL_FOR_STREAMING)):
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
        self.entity_types = entity_types

    def stream(self):
        if self.start_block is not None or not os.path.isfile(self.last_synced_block_file):
            init_last_synced_block_file((self.start_block or 0) - 1, self.last_synced_block_file)

        last_synced_block = read_last_synced_block(self.last_synced_block_file)

        self.item_exporter.open()

        while True and (self.end_block is None or last_synced_block < self.end_block):
            new_last_synced_block = last_synced_block

            try:
                new_last_synced_block = self._sync_cycle(last_synced_block)
            except Exception as e:
                # https://stackoverflow.com/a/4992124/1580227
                logging.exception('An exception occurred while fetching block data.')

            synced_blocks = new_last_synced_block - last_synced_block
            last_synced_block = new_last_synced_block
            if synced_blocks <= 0:
                logging.info('Nothing to sync or exception. Sleeping for {} seconds...'.format(self.period_seconds))
                time.sleep(self.period_seconds)

        self.item_exporter.close()

    @timeout_decorator.timeout(900)
    def _sync_cycle(self, last_synced_block):
        current_block = int(Web3(self.batch_web3_provider).eth.getBlock("latest").number)
        target_block = self._calculate_target_block(current_block, last_synced_block)
        blocks_to_sync = max(target_block - last_synced_block, 0)

        logging.info('Current block {}, target block {}, last synced block {}, blocks to sync {}'.format(
            current_block, target_block, last_synced_block, blocks_to_sync))

        if blocks_to_sync != 0:
            self._export_all(last_synced_block + 1, target_block)
            logging.info('Writing last synced block {}'.format(target_block))
            write_last_synced_block(self.last_synced_block_file, target_block)
            last_synced_block = target_block

        return last_synced_block

    def _calculate_target_block(self, current_block, last_synced_block):
        target_block = current_block - self.lag
        target_block = min(target_block, last_synced_block + self.block_batch_size)
        target_block = min(target_block, self.end_block) if self.end_block is not None else target_block
        return target_block

    def _export_all(self, start_block, end_block):
        # Export blocks and transactions
        blocks, transactions = [], []
        if self._should_export(EntityType.BLOCK) or self._should_export(EntityType.TRANSACTION):
            blocks, transactions = self._export_blocks_and_transactions(start_block, end_block)

        # Export receipts and logs
        receipts, logs = [], []
        if self._should_export(EntityType.RECEIPT) or self._should_export(EntityType.LOG):
            receipts, logs = self._export_receipts_and_logs(transactions)

        # Extract token transfers
        token_transfers = []
        if self._should_export(EntityType.TOKEN_TRANSFER):
            token_transfers = self._extract_token_transfers(logs)

        # Export traces
        traces = []
        if self._should_export(EntityType.TRACE):
            traces = self._export_traces(start_block, end_block)

        # Export contracts
        contracts = []
        if self._should_export(EntityType.CONTRACT):
            contracts = self._export_contracts(traces)

        # Export tokens
        tokens = []
        if self._should_export(EntityType.TOKEN):
            tokens = self._export_tokens(contracts)

        enriched_transactions = enrich_transactions(blocks, transactions, receipts)
        enriched_logs = enrich_logs(blocks, logs)
        enriched_token_transfers = enrich_token_transfers(blocks, token_transfers)
        enriched_traces = enrich_traces(blocks, traces)
        enriched_contracts = enrich_contracts(blocks, contracts)

        logging.info('Publishing to PubSub')

        self.item_exporter.export_items(
            (blocks if EntityType.BLOCK in self.entity_types else []) +
            (enriched_transactions if EntityType.TRANSACTION in self.entity_types else []) +
            (enriched_logs if EntityType.LOG in self.entity_types else []) +
            (enriched_token_transfers if EntityType.TOKEN_TRANSFER in self.entity_types else []) +
            (enriched_traces if EntityType.TRACE in self.entity_types else []) +
            (enriched_contracts if EntityType.CONTRACT in self.entity_types else []) +
            (tokens if EntityType.TOKEN in self.entity_types else [])
        )

    def _export_blocks_and_transactions(self, start_block, end_block):
        blocks_and_transactions_item_exporter = InMemoryItemExporter(item_types=['block', 'transaction'])
        blocks_and_transactions_job = ExportBlocksJob(
            start_block=start_block,
            end_block=end_block,
            batch_size=self.batch_size,
            batch_web3_provider=self.batch_web3_provider,
            max_workers=self.max_workers,
            item_exporter=blocks_and_transactions_item_exporter,
            export_blocks=self._should_export(EntityType.BLOCK),
            export_transactions=self._should_export(EntityType.TRANSACTION)
        )
        blocks_and_transactions_job.run()
        blocks = blocks_and_transactions_item_exporter.get_items('block')
        transactions = blocks_and_transactions_item_exporter.get_items('transaction')
        return blocks, transactions

    def _export_receipts_and_logs(self, transactions):
        exporter = InMemoryItemExporter(item_types=['receipt', 'log'])
        job = ExportReceiptsJob(
            transaction_hashes_iterable=(transaction['hash'] for transaction in transactions),
            batch_size=self.batch_size,
            batch_web3_provider=self.batch_web3_provider,
            max_workers=self.max_workers,
            item_exporter=exporter,
            export_receipts=self._should_export(EntityType.RECEIPT),
            export_logs=self._should_export(EntityType.LOG)
        )
        job.run()
        receipts = exporter.get_items('receipt')
        logs = exporter.get_items('log')
        return receipts, logs

    def _extract_token_transfers(self, logs):
        exporter = InMemoryItemExporter(item_types=['token_transfer'])
        job = ExtractTokenTransfersJob(
            logs_iterable=logs,
            batch_size=self.batch_size,
            max_workers=self.max_workers,
            item_exporter=exporter)
        job.run()
        token_transfers = exporter.get_items('token_transfer')
        return token_transfers

    def _export_traces(self, start_block, end_block):
        exporter = InMemoryItemExporter(item_types=['trace'])
        job = ExportTracesJob(
            start_block=start_block,
            end_block=end_block,
            batch_size=self.batch_size,
            web3=ThreadLocalProxy(lambda: Web3(self.batch_web3_provider)),
            max_workers=self.max_workers,
            item_exporter=exporter
        )
        job.run()
        traces = exporter.get_items('trace')
        return traces

    def _export_contracts(self, traces):
        exporter = InMemoryItemExporter(item_types=['contract'])
        job = ExtractContractsJob(
            traces_iterable=traces,
            batch_size=self.batch_size,
            max_workers=self.max_workers,
            item_exporter=exporter
        )
        job.run()
        contracts = exporter.get_items('contract')
        return contracts

    def _export_tokens(self, contracts):
        token_addresses = (contract['address'] for contract in contracts
                           if contract['is_erc20'] or contract['is_erc721'])

        exporter = InMemoryItemExporter(item_types=['token'])
        job = ExportTokensJob(
            token_addresses_iterable=token_addresses,
            web3=ThreadLocalProxy(lambda: Web3(self.batch_web3_provider)),
            max_workers=self.max_workers,
            item_exporter=exporter
        )
        job.run()
        tokens = exporter.get_items('token')
        return tokens

    def _should_export(self, entity_type):
        if entity_type == EntityType.BLOCK:
            return True

        if entity_type == EntityType.TRANSACTION:
            return EntityType.TRANSACTION in self.entity_types or self._should_export(EntityType.LOG)

        if entity_type == EntityType.RECEIPT:
            return EntityType.TRANSACTION in self.entity_types or self._should_export(EntityType.TOKEN_TRANSFER)

        if entity_type == EntityType.LOG:
            return EntityType.LOG in self.entity_types or self._should_export(EntityType.TOKEN_TRANSFER)

        if entity_type == EntityType.TOKEN_TRANSFER:
            return EntityType.TOKEN_TRANSFER in self.entity_types

        if entity_type == EntityType.TRACE:
            return EntityType.TRACE in self.entity_types or self._should_export(EntityType.CONTRACT)

        if entity_type == EntityType.CONTRACT:
            return EntityType.CONTRACT in self.entity_types or self._should_export(EntityType.TOKEN)

        if entity_type == EntityType.TOKEN:
            return EntityType.TOKEN in self.entity_types

        raise ValueError('Unexpected entity type ' + entity_type)


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
