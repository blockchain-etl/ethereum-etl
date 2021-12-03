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


import json
from collections import OrderedDict
from operator import itemgetter

from blockchainetl.jobs.base_job import BaseJob
from ethereumetl.executors.batch_work_executor import BatchWorkExecutor
from ethereumetl.json_rpc_requests import generate_get_balances_json_rpc
from ethereumetl.json_rpc_requests import generate_get_block_by_number_json_rpc
from ethereumetl.mappers.balance_mapper import EthBalanceMapper
from ethereumetl.mappers.block_mapper import EthBlockMapper
from ethereumetl.utils import rpc_response_batch_to_results, validate_range


# Exports balances
class ExportBalancesJob(BaseJob):
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
        self.block_mapper = EthBlockMapper()
        self.balance_mapper = EthBalanceMapper()

    def _start(self):
        self.item_exporter.open()

    def _export(self):
        self.batch_work_executor.execute(
            range(self.start_block, self.end_block + 1),
            self._export_batch,
            total_items=self.end_block - self.start_block + 1
        )

    def _export_batch(self, block_number_batch):
        blocks_rpc = list(generate_get_block_by_number_json_rpc(block_number_batch, True))
        response = self.batch_web3_provider.make_batch_request(json.dumps(blocks_rpc))
        results = rpc_response_batch_to_results(response)
        blocks = [self.block_mapper.json_dict_to_block(result) for result in results]
        balance_params = self._get_balance_params(blocks)
        balances = self._get_balances((itemgetter(0, 1)(param) for param in balance_params))
        self._export_balances(balance_params, balances)

    def _get_balance_params(self, blocks):
        d = OrderedDict()
        for block in blocks:
            d[(block.miner, block.number, block.hash)] = True
            for tx in block.transactions:
                d[(tx.from_address, block.number, block.hash)] = True
                if tx.to_address is not None:
                    d[(tx.to_address, block.number, block.hash)] = True
        return d.keys()

    def _get_balances(self, address_with_block_numbers):
        balances_rpc = list(generate_get_balances_json_rpc(address_with_block_numbers))
        response = self.batch_web3_provider.make_batch_request(json.dumps(balances_rpc))
        return rpc_response_batch_to_results(response)

    def _export_balances(self, balance_params, balances):
        for address, block_number, block_hash in balance_params:
            args = (block_number, block_hash, address, next(balances))
            balance = self.balance_mapper.transaction_to_balance(*args)
            self.item_exporter.export_item(self.balance_mapper.balance_to_dict(balance))

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()
