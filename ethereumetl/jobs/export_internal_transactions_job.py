# MIT License
#
# Copyright (c) 2018 Evgeniy Filatov, evgeniyfilatov@gmail.com
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
from ethereumetl.jobs.base_job import BaseJob
from ethereumetl.utils import validate_range
from ethereumetl.mappers.internal_transaction_mapper import EthInternalTransactionMapper


class ExportInternalTransactionsJob(BaseJob):
    def __init__(
            self,
            start_block,
            end_block,
            batch_size,
            web3,
            item_exporter,
            max_workers):
        validate_range(start_block, end_block)
        self.start_block = start_block
        self.end_block = end_block

        self.web3 = web3

        self.batch_work_executor = BatchWorkExecutor(batch_size, max_workers)
        self.item_exporter = item_exporter

        self.internal_transaction_mapper = EthInternalTransactionMapper()

    def _start(self):
        self.item_exporter.open()

    def _export(self):
        self.batch_work_executor.execute(
            range(self.start_block, self.end_block + 1),
            self._export_batch,
            total_items=self.end_block - self.start_block + 1
        )

    def _export_batch(self, block_number_batch):
        assert len(block_number_batch) > 0

        filter_params = {
            'fromBlock': hex(block_number_batch[0]),
            'toBlock': hex(block_number_batch[-1]),
        }

        traces = self.web3.parity.traceFilter(filter_params)

        for trace in traces:
            # skip reward tracces
            if trace.get('type', None) == 'reward':
                continue

            # skip non-internal transactions
            if not trace.get('traceAddress', []):
                continue

            internal_transaction = self.internal_transaction_mapper.json_dict_to_internal_transaction(trace)
            self.item_exporter.export_item(self.internal_transaction_mapper.internal_transaction_to_dict(internal_transaction))

    def _end(self):
        self.batch_work_executor.shutdown()
