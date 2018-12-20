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

import time
from web3 import Web3

from ethereumetl.executors.repeated_executor import RepeatedExecutor
from ethereumetl.jobs.base_job import BaseJob
from ethereumetl.mappers.pending_transaction_mapper import EthPendingTransactionMapper


# Exports pending transactions
class ExportPendingTransactionsJob(BaseJob):
    def __init__(
            self,
            web3_provider,
            item_exporter,
            export_pending_transactions=True):

        self.web3_provider = web3_provider
        self.web3 = Web3(web3_provider)
        self.pending_transaction_filter = self.web3.eth.filter('pending')

        self.repeated_executor = RepeatedExecutor(1, self._get_new_pending_transaction)

        self.item_exporter = item_exporter

        self.export_pending_transactions = export_pending_transactions
        if not self.export_pending_transactions:
            raise ValueError('export_pending_transactions must be True')

        self.pending_transaction_mapper = EthPendingTransactionMapper()

    def _start(self):
        self.item_exporter.open()

    def _export(self):
        self.repeated_executor.start()

    def _get_new_pending_transaction(self):
        results = self.pending_transaction_filter.get_new_entries()
        pending_transactions = [self.pending_transaction_mapper.hash_to_pending_transaction(result)
                                for result in results]

        for pending_transaction in pending_transactions:
            # Set current local timestamp
            pending_transaction.timestamp = time.time()
            print(pending_transaction.hash)
            print(pending_transaction.timestamp)
            self._export_pending_transaction_item(pending_transaction)

    def _export_pending_transaction_item(self, pending_transaction):
        if self.export_pending_transactions:
            self.item_exporter.export_item(
                self.pending_transaction_mapper.pending_transaction_to_dict(pending_transaction)
            )

    def _end(self):
        pass
        # self.repeated_executor.stop()
        # self.item_exporter.close()

    def stop(self):
        self.repeated_executor.stop()
        self.item_exporter.close()
