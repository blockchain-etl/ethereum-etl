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


from ethereumetl.domain.pending_transaction import EthPendingTransaction
# from ethereumetl.utils import hex_to_dec, to_normalized_address


class EthPendingTransactionMapper(object):
    def hash_to_pending_transaction(self, tx_hash):
        pending_transaction = EthPendingTransaction()
        pending_transaction.hash = tx_hash.hex()
        pending_transaction.timestamp = None

        return pending_transaction

    def json_dict_to_pending_transaction(self, json_dict):
        pending_transaction = EthPendingTransaction()
        pending_transaction.hash = json_dict.get('hash', None)
        pending_transaction.timestamp = json_dict.get('timestamp', None)

        return pending_transaction

        """Do not remove, it might be used to enrich pending transaction data"""
        # pending_transaction = EthPendingTransaction()
        # pending_transaction.hash = json_dict.get('hash', None)
        # pending_transaction.nonce = hex_to_dec(json_dict.get('nonce', None))
        # pending_transaction.block_hash = json_dict.get('blockHash', None)
        # pending_transaction.block_number = hex_to_dec(json_dict.get('blockNumber', None))
        # pending_transaction.transaction_index = hex_to_dec(json_dict.get('transactionIndex', None))
        # pending_transaction.from_address = to_normalized_address(json_dict.get('from', None))
        # pending_transaction.to_address = to_normalized_address(json_dict.get('to', None))
        # pending_transaction.value = hex_to_dec(json_dict.get('value', None))
        # pending_transaction.gas = hex_to_dec(json_dict.get('gas', None))
        # pending_transaction.gas_price = hex_to_dec(json_dict.get('gasPrice', None))
        # pending_transaction.input = json_dict.get('input', None)
        # pending_transaction.timestamp = json_dict.get('timestamp', None)
        # return pending_transaction

    def pending_transaction_to_dict(self, pending_transaction):
        return {
            'type': 'pending_transaction',
            'hash': pending_transaction.hash,
            'timestamp': pending_transaction.timestamp
        }

        """Do not remove, it must be used to enrich pending transaction data"""
        # 'nonce': pending_transaction.nonce,
        # 'block_hash': pending_transaction.block_hash,
        # 'block_number': pending_transaction.block_number,
        # 'transaction_index': pending_transaction.transaction_index,
        # 'from_address': pending_transaction.from_address,
        # 'to_address': pending_transaction.to_address,
        # 'value': pending_transaction.value,
        # 'gas': pending_transaction.gas,
        # 'gas_price': pending_transaction.gas_price,
        # 'input': pending_transaction.input,

