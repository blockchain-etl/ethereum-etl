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


from ethereumetl.domain.transaction import EthTransaction
from ethereumetl.utils import hex_to_dec, to_normalized_address


class EthTransactionMapper(object):
    def json_dict_to_transaction(self, json_dict):
        transaction = EthTransaction()
        transaction.hash = json_dict.get('hash', None)
        transaction.nonce = hex_to_dec(json_dict.get('nonce', None))
        transaction.block_hash = json_dict.get('blockHash', None)
        transaction.block_number = hex_to_dec(json_dict.get('blockNumber', None))
        transaction.transaction_index = hex_to_dec(json_dict.get('transactionIndex', None))
        transaction.from_address = to_normalized_address(json_dict.get('from', None))
        transaction.to_address = to_normalized_address(json_dict.get('to', None))
        transaction.value = hex_to_dec(json_dict.get('value', None))
        transaction.gas = hex_to_dec(json_dict.get('gas', None))
        transaction.gas_price = hex_to_dec(json_dict.get('gasPrice', None))
        transaction.input = json_dict.get('input', None)
        return transaction

    def transaction_to_dict(self, transaction):
        return {
            'type': 'transaction',
            'hash': transaction.hash,
            'nonce': transaction.nonce,
            'block_hash': transaction.block_hash,
            'block_number': transaction.block_number,
            'transaction_index': transaction.transaction_index,
            'from_address': transaction.from_address,
            'to_address': transaction.to_address,
            'value': transaction.value,
            'gas': transaction.gas,
            'gas_price': transaction.gas_price,
            'input': transaction.input,
        }
