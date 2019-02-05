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
import json
from web3 import Web3

from ethereumetl.executors.repeated_executor import RepeatedExecutor
from ethereumetl.jobs.base_job import BaseJob
from ethereumetl.mappers.pending_transaction_mapper import EthPendingTransactionMapper
from ethereumetl.json_rpc_requests import \
    generate_pending_transaction_filter_json_rpc, \
    generate_get_new_entries_json_rpc, \
    generate_get_transaction_json_rpc
from ethereumetl.utils import rpc_response_batch_to_results, safe_rpc_response_batch_to_results


# Exports pending transactions
class ExportPendingTransactionsJob(BaseJob):
    def __init__(
            self,
            batch_web3_provider,
            item_exporter,
            export_pending_transactions=True):

        self.batch_web3_provider = batch_web3_provider
        self.web3 = Web3(batch_web3_provider)

        self.pending_transaction_filter_id = self._generate_pending_transaction_filter()
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
        pending_transaction_hashes = self._get_new_pending_transaction_hashes()
        if len(pending_transaction_hashes) == 0:
            return
        timestamp = time.time()
        print(pending_transaction_hashes, timestamp)
        filter_rpc = list(generate_get_transaction_json_rpc(pending_transaction_hashes))
        response = self.batch_web3_provider.make_request(json.dumps(filter_rpc))
        results = safe_rpc_response_batch_to_results(response)
        pending_transactions = [self.pending_transaction_mapper.json_dict_to_pending_transaction(result)
                                for result in results]

        for pending_transaction in pending_transactions:
            pending_transaction.timestamp = timestamp
            self._export_pending_transaction_item(pending_transaction)

    def _export_pending_transaction_item(self, pending_transaction):
        if self.export_pending_transactions:
            self.item_exporter.export_item(
                self.pending_transaction_mapper.pending_transaction_to_dict(pending_transaction)
            )

    def _generate_pending_transaction_filter(self):
        filter_rpc = list(generate_pending_transaction_filter_json_rpc())
        response = self.batch_web3_provider.make_request(json.dumps(filter_rpc))
        results = rpc_response_batch_to_results(response)
        return next(results)

    def _get_new_pending_transaction_hashes(self):
        filter_rpc = list(generate_get_new_entries_json_rpc(self.pending_transaction_filter_id))
        response = self.batch_web3_provider.make_request(json.dumps(filter_rpc))
        results = rpc_response_batch_to_results(response)
        return next(results)

    def _end(self):
        pass
        # self.repeated_executor.stop()
        # self.item_exporter.close()

    def stop(self):
        self.repeated_executor.stop()
        self.item_exporter.close()
