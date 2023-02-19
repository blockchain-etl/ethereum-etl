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


from ethereumetl.domain.contract import EthContract
from ethereumetl.executors.batch_work_executor import BatchWorkExecutor
from blockchainetl.jobs.base_job import BaseJob
from ethereumetl.mappers.contract_mapper import EthContractMapper

from ethereumetl.service.eth_contract_service import EthContractService
from ethereumetl.utils import to_int_or_none


# Extract contracts
class ExtractContractsJob(BaseJob):
    def __init__(
            self,
            traces_iterable,
            batch_size,
            max_workers,
            item_exporter):
        self.traces_iterable = traces_iterable

        self.batch_work_executor = BatchWorkExecutor(batch_size, max_workers)
        self.item_exporter = item_exporter

        self.contract_service = EthContractService()
        self.contract_mapper = EthContractMapper()

    def _start(self):
        self.item_exporter.open()

    def _export(self):
        self.batch_work_executor.execute(self.traces_iterable, self._extract_contracts)

    def _extract_contracts(self, traces):
        contract_creation_traces = []

        # Geth returns traces as a tree starting with the top-level transactions
        def process_call(transaction_trace, block_number):
            if "calls" in transaction_trace:
                for sub_call in transaction_trace["calls"]:
                    process_call(sub_call, block_number)

            # CREATE vs CREATE2: https://blog.cotten.io/ethereums-eip-1014-create-2-d17b1a184498
            if transaction_trace["type"].lower() == "create" or transaction_trace["type"].lower() == "create2":
                if "error" in transaction_trace:
                    return
                if len(transaction_trace["to"]) == 0:
                    return
                transaction_trace["block_number"] = block_number
                contract_creation_traces.append(transaction_trace)

        for geth_block_trace in traces:
            trace_block_number = geth_block_trace["block_number"]
            for transaction_trace in geth_block_trace["transaction_traces"]:
                process_call(transaction_trace, trace_block_number)

        contracts = []
        for trace in contract_creation_traces:
            contract = EthContract()
            contract.address = trace["to"]
            contract.block_number = trace['block_number']

            bytecode = None
            if "output" in trace:
                bytecode = trace['output']
                contract.bytecode = bytecode

            function_sighashes = self.contract_service.get_function_sighashes(bytecode)
            contract.function_sighashes = function_sighashes
            contract.is_erc20 = self.contract_service.is_erc20_contract(function_sighashes)
            contract.is_erc721 = self.contract_service.is_erc721_contract(function_sighashes)

            contracts.append(contract)

        for contract in contracts:
            self.item_exporter.export_item(self.contract_mapper.contract_to_dict(contract))

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()
