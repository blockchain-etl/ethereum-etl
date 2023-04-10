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

from ethereumetl.executors.batch_work_executor import BatchWorkExecutor
from blockchainetl.jobs.base_job import BaseJob
from ethereumetl.mappers.token_transfer_mapper import EthTokenTransferMapper
from ethereumetl.mappers.receipt_log_mapper import EthReceiptLogMapper
from ethereumetl.mappers.transaction_mapper import EthTransactionMapper
from ethereumetl.service.token_transfer_extractor import EthTokenTransferExtractor


class ExtractTokenTransfersJob(BaseJob):
    def __init__(
            self,
            logs_iterable,
            batch_size,
            max_workers,
            item_exporter,
            transactions_iterable=None,
        ):
        self.logs_iterable = logs_iterable
        self.transactions_iterable = transactions_iterable if transactions_iterable is not None else []

        self.batch_work_executor = BatchWorkExecutor(batch_size, max_workers)
        self.item_exporter = item_exporter

        self.receipt_log_mapper = EthReceiptLogMapper()
        self.token_transfer_mapper = EthTokenTransferMapper()
        self.token_transfer_extractor = EthTokenTransferExtractor()
        self.transactions_mapper = EthTransactionMapper()   

    def _start(self):
        self.item_exporter.open()

    def _export(self):
        self.batch_work_executor.execute(self.logs_iterable, self._extract_transfers)
        self.batch_work_executor.execute(self.transactions_iterable, self._extract_transfers_from_txn)

    def _extract_transfers(self, log_dicts):        
        for log_dict in log_dicts:
            self._extract_transfer(log_dict)

    def _extract_transfers_from_txn(self, transaction_dicts):        
        for transaction_dict in transaction_dicts:
            txn_hash = transaction_dict.get('hash')
            txn_logs = [log_dict for log_dict in self.logs_iterable if log_dict['transaction_hash'].lower() == txn_hash.lower()]
            self._extract_transfer_from_txn(transaction_dict, txn_logs)

    def _extract_transfer_from_txn(self, transaction_dict, txn_logs):
        token_transfer = self.token_transfer_extractor.extract_transfer_from_transaction(transaction_dict, txn_logs)
        if token_transfer is not None:
            self.item_exporter.export_item(self.token_transfer_mapper.token_transfer_to_dict(token_transfer))

    def _extract_transfer(self, log_dict):
        log = self.receipt_log_mapper.dict_to_receipt_log(log_dict)
        token_transfer = self.token_transfer_extractor.extract_transfer_from_log(log)
        if token_transfer is not None:
            self.item_exporter.export_item(self.token_transfer_mapper.token_transfer_to_dict(token_transfer))

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()
