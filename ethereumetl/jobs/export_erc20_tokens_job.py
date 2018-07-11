from web3.exceptions import BadFunctionCallOutput

from ethereumetl.executors.batch_work_executor import BatchWorkExecutor
from ethereumetl.jobs.base_job import BaseJob
from ethereumetl.mappers.erc20_token_mapper import EthErc20TokenMapper
from ethereumetl.service.erc20_token_service import EthErc20TokenService


class ExportErc20TokensJob(BaseJob):
    def __init__(self, web3, item_exporter, token_addresses_iterable, max_workers):
        self.web3 = web3
        self.item_exporter = item_exporter
        self.token_addresses_iterable = token_addresses_iterable
        self.batch_work_executor = BatchWorkExecutor(1, max_workers)

        # BadFunctionCallOutput exception happens if the token doesn't implement a particular function
        # or was self-destructed
        # OverflowError exception happens if the return type of the function doesn't match the expected type
        self.erc20_token_service = EthErc20TokenService(self.web3, ignore_errors=(BadFunctionCallOutput, OverflowError))
        self.erc20_token_mapper = EthErc20TokenMapper()

    def _start(self):
        self.item_exporter.open()

    def _export(self):
        self.batch_work_executor.execute(self.token_addresses_iterable, self._export_tokens)

    def _export_tokens(self, token_addresses):
        for token_address in token_addresses:
            self._export_token(token_address)

    def _export_token(self, token_address):
        token = self.erc20_token_service.get_token(token_address)
        token_dict = self.erc20_token_mapper.erc20_token_to_dict(token)
        self.item_exporter.export_item(token_dict)

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()
