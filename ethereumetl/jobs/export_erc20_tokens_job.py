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

        symbol = self._call_contract_function(contract.functions.symbol())
        name = self._call_contract_function(contract.functions.name())
        decimals = self._call_contract_function(contract.functions.decimals())
        total_supply = self._call_contract_function(contract.functions.totalSupply())

        token = EthErc20Token()
        token.erc20_token_address = token_address
        token.erc20_token_symbol = symbol
        token.erc20_token_name = name
        token.erc20_token_decimals = decimals
        token.erc20_token_total_supply = total_supply

        token_dict = self.erc20_token_mapper.erc20_token_to_dict(token)
        self.item_exporter.export_item(token_dict)

    def _call_contract_function(self, func):
        # BadFunctionCallOutput exception happens if the token doesn't implement a particular function
        # or was self-destructed
        # OverflowError exception happens if the return type of the function doesn't match the expected type
        result = call_contract_function(
            func=func,
            ignore_errors=(BadFunctionCallOutput, OverflowError),
            default_value=None)

        return clean_user_provided_content(result)

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()


def call_contract_function(func, ignore_errors, default_value=None):
    try:
        result = func.call()
        return result
    except Exception as ex:
        if type(ex) in ignore_errors:
            return default_value
        else:
            raise ex


# https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types#numeric-type
NUMERIC_MAX_VALUE = 99999999999999999999999999999
ASCII_0 = 0


def clean_user_provided_content(content):
    if isinstance(content, str):
        # This prevents this error in BigQuery
        # Error while reading data, error message: Error detected while parsing row starting at position: 9999.
        # Error: Bad character (ASCII 0) encountered.
        return content.translate({ASCII_0: None})
    elif isinstance(content, int):
        # NUMERIC type in BigQuery is 16 bytes
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types#numeric-type
        return content if content <= NUMERIC_MAX_VALUE else None
    else:
        return content
