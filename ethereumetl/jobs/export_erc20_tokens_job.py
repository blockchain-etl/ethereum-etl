from ethtoken.abi import EIP20_ABI
from web3.exceptions import BadFunctionCallOutput

from ethereumetl.domain.erc20_token import EthErc20Token
from ethereumetl.executors.batch_work_executor import BatchWorkExecutor
from ethereumetl.jobs.base_job import BaseJob
from ethereumetl.mappers.erc20_token_mapper import EthErc20TokenMapper


class ExportErc20TokensJob(BaseJob):
    def __init__(self, web3, item_exporter, token_addresses_iterable, max_workers):
        self.web3 = web3
        self.item_exporter = item_exporter
        self.token_addresses_iterable = token_addresses_iterable
        self.batch_work_executor = BatchWorkExecutor(1, max_workers)
        self.erc20_token_mapper = EthErc20TokenMapper()

    def _start(self):
        self.item_exporter.open()

    def _export(self):
        self.batch_work_executor.execute(self.token_addresses_iterable, self._export_tokens)

    def _export_tokens(self, token_addresses):
        for token_address in token_addresses:
            self._export_token(token_address)

    def _export_token(self, token_address):
        checksum_address = self.web3.toChecksumAddress(token_address)
        contract = self.web3.eth.contract(address=checksum_address, abi=EIP20_ABI)

        symbol = self._call_function(contract.functions.symbol())
        name = self._call_function(contract.functions.name())
        decimals = self._call_function(contract.functions.decimals())
        total_supply = self._call_function(contract.functions.totalSupply())

        token = EthErc20Token()
        token.erc20_token_address = token_address
        token.erc20_token_symbol = symbol
        token.erc20_token_name = name
        token.erc20_token_decimals = decimals
        token.erc20_token_total_supply = total_supply

        token_dict = self.erc20_token_mapper.erc20_token_to_dict(token)
        self.item_exporter.export_item(token_dict)

    def _call_function(self, func):
        try:
            return func.call()
        except BadFunctionCallOutput as ex:
            return "Error: BadFunctionCallOutput - {}".format(str(ex))

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()
