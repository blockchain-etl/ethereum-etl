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

from ethereumetl.executors.batch_work_executor import BatchWorkExecutor
from ethereumetl.jobs.base_job import BaseJob
from ethereumetl.json_rpc_requests import generate_get_code_json_rpc
from ethereumetl.mappers.contract_mapper import EthContractMapper


# Exports contracts bytecode
class ExportContractsJob(BaseJob):
    def __init__(
            self,
            contract_addresses_iterable,
            batch_size,
            ipc_wrapper,
            max_workers,
            item_exporter):
        self.ipc_wrapper = ipc_wrapper
        self.contract_addresses_iterable = contract_addresses_iterable

        self.batch_work_executor = BatchWorkExecutor(batch_size, max_workers)
        self.item_exporter = item_exporter

        self.contract_mapper = EthContractMapper()

    def _start(self):
        self.item_exporter.open()

    def _export(self):
        self.batch_work_executor.execute(self.contract_addresses_iterable, self._export_contracts)

    def _export_contracts(self, contract_addresses):
        contracts_code_rpc = list(generate_get_code_json_rpc(contract_addresses))
        response_batch= self.ipc_wrapper.make_request(json.dumps(contracts_code_rpc))

        contracts = []
        for response in response_batch:
            # request id is the index of the contract address in contract_addresses list
            request_id = response['id']
            result = response['result']

            contract_address = contract_addresses[request_id]
            contracts.append(self.contract_mapper.rpc_result_to_receipt(contract_address, result))

        for contract in contracts:
            self.item_exporter.export_item(self.contract_mapper.contract_to_dict(contract))

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()
