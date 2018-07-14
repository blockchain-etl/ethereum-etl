from web3.exceptions import BadFunctionCallOutput

from ethereumetl.domain.erc20_token import EthErc20Token
from ethereumetl.erc20_abi import ERC20_ABI


class EthErc20TokenService(object):
    def __init__(self, web3, function_call_result_transformer=None):
        self._web3 = web3
        self._function_call_result_transformer = function_call_result_transformer

    def get_token(self, token_address):
        checksum_address = self._web3.toChecksumAddress(token_address)
        contract = self._web3.eth.contract(address=checksum_address, abi=ERC20_ABI)

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

        return token

    def _call_contract_function(self, func):
        # BadFunctionCallOutput exception happens if the token doesn't implement a particular function
        # or was self-destructed
        # OverflowError exception happens if the return type of the function doesn't match the expected type
        result = call_contract_function(
            func=func,
            ignore_errors=(BadFunctionCallOutput, OverflowError),
            default_value=None)

        if self._function_call_result_transformer is not None:
            return self._function_call_result_transformer(result)
        else:
            return result


def call_contract_function(func, ignore_errors, default_value=None):
    try:
        result = func.call()
        return result
    except Exception as ex:
        if type(ex) in ignore_errors:
            return default_value
        else:
            raise ex
