from ethereumetl.domain.transaction import EthTransaction
from ethereumetl.utils import hex_to_dec, to_normalized_address


class EthTransactionMapper(object):
    def json_dict_to_transaction(self, json_dict):
        transaction = EthTransaction()
        transaction.hash = json_dict.get('hash', None)
        transaction.nonce = hex_to_dec(json_dict.get('nonce', None))
        transaction.block_hash = json_dict.get('blockHash', None)
        transaction.block_number = hex_to_dec(json_dict.get('blockNumber', None))
        transaction.index = hex_to_dec(json_dict.get('transactionIndex', None))
        transaction.from_address = to_normalized_address(json_dict.get('from', None))
        transaction.to_address = to_normalized_address(json_dict.get('to', None))
        transaction.value = hex_to_dec(json_dict.get('value', None))
        transaction.gas = hex_to_dec(json_dict.get('gas', None))
        transaction.gas_price = hex_to_dec(json_dict.get('gasPrice', None))
        transaction.input = json_dict.get('input', None)
        return transaction

    def transaction_to_dict(self, transaction):
        return {
            'tx_hash': transaction.hash,
            'tx_nonce': transaction.nonce,
            'tx_block_hash': transaction.block_hash,
            'tx_block_number': transaction.block_number,
            'tx_index': transaction.index,
            'tx_from': transaction.from_address,
            'tx_to': transaction.to_address,
            'tx_value': transaction.value,
            'tx_gas': transaction.gas,
            'tx_gas_price': transaction.gas_price,
            'tx_input': transaction.input,
        }
