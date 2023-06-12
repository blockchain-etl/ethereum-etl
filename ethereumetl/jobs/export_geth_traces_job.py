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

import json

from ethereumetl.executors.batch_work_executor import BatchWorkExecutor
from ethereumetl.jobs.export_traces_job import calculate_trace_indexes
from ethereumetl.json_rpc_requests import generate_trace_block_by_number_json_rpc, generate_get_block_by_number_json_rpc
from blockchainetl.jobs.base_job import BaseJob
from ethereumetl.mappers.geth_trace_mapper import EthGethTraceMapper
from ethereumetl.mappers.trace_mapper import EthTraceMapper
from ethereumetl.service.trace_id_calculator import calculate_trace_ids, trace_address_to_str
from ethereumetl.service.trace_status_calculator import calculate_trace_statuses
from ethereumetl.utils import validate_range, rpc_response_to_result


# Exports geth traces
class ExportGethTracesJob(BaseJob):
    def __init__(
            self,
            start_block,
            end_block,
            batch_size,
            batch_web3_provider,
            max_workers,
            item_exporter):
        validate_range(start_block, end_block)
        self.start_block = start_block
        self.end_block = end_block

        self.batch_web3_provider = batch_web3_provider

        self.batch_work_executor = BatchWorkExecutor(batch_size, max_workers)
        self.item_exporter = item_exporter

        self.geth_trace_mapper = EthGethTraceMapper()
        self.mapper = EthTraceMapper()

    def _start(self):
        self.item_exporter.open()

    def _export(self):
        self.batch_work_executor.execute(
            range(self.start_block, self.end_block + 1),
            self._export_batch,
            total_items=self.end_block - self.start_block + 1
        )

    def _export_batch(self, block_number_batch):
        trace_block_rpc = list(generate_trace_block_by_number_json_rpc(block_number_batch))
        trace_response = self.batch_web3_provider.make_batch_request(json.dumps(trace_block_rpc))
        block_rpc = list(generate_get_block_by_number_json_rpc(block_number_batch, True))
        block_response = self.batch_web3_provider.make_batch_request(json.dumps(block_rpc))
        trace_response.sort(key=lambda x: x["id"])
        block_response.sort(key=lambda x: x["id"])

        for block_idx, response_item in enumerate(trace_response):
            block_number = response_item.get('id')
            traces_result = rpc_response_to_result(response_item)
            transactions_result = rpc_response_to_result(block_response[block_idx]).get('transactions')
            geth_trace = self.geth_trace_mapper.json_dict_to_geth_trace({
                'block_number': block_number,
                'transaction_traces': [tx_trace.get('result') for tx_trace in traces_result]
            })
            traces = self.mapper.geth_trace_to_traces(geth_trace)
            for tx_idx, trace in enumerate(traces):
                if trace.value is None:
                    trace.value = 0
                trace.transaction_hash = transactions_result[trace.transaction_index].get('hash')
            calculate_trace_statuses(traces)
            calculate_trace_ids(traces)
            calculate_trace_indexes(traces)
            for trace in traces:
                trace = self.mapper.trace_to_dict(trace)
                trace['type'] = 'geth_trace'
                trace['trace_address'] = trace_address_to_str(trace['trace_address'])
                self.item_exporter.export_item(trace)



    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()
