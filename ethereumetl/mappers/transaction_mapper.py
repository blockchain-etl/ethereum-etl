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
    def json_dict_to_transaction(self, json_dict, **kwargs):
        transaction = EthTransaction()
        transaction.block_hash = kwargs.get('block_hash')
        transaction.block_number = kwargs.get('block_number')
        transaction.block_timestamp = kwargs.get('block_timestamp')
        transaction.class_hash = json_dict.get('class_hash')
        transaction.constructor_calldata = json_dict.get('constructor_calldata')
        transaction.contract_address_salt = json_dict.get('contract_address_salt')
        transaction.transaction_hash = json_dict.get('transaction_hash')
        transaction.transaction_type = json_dict.get('type')
        transaction.version = json_dict.get('version')
        transaction.calldata = json_dict.get('calldata')
        transaction.contract_address = json_dict.get('contract_address')
        transaction.entry_point_selector = json_dict.get('entry_point_selector')
        transaction.max_fee = hex_to_dec(json_dict.get('max_fee'))
        transaction.nonce = hex_to_dec(json_dict.get('nonce'))
        transaction.signature = json_dict.get('signature')
        transaction.sender_address = json_dict.get('sender_address')
        return transaction

    def transaction_to_dict(self, transaction):
        return {
            'type': 'transaction',
            'block_hash': transaction.block_hash,
            'block_number': transaction.block_number,
            'block_timestamp': transaction.block_timestamp,
            'class_hash': transaction.class_hash,
            'constructor_calldata': transaction.constructor_calldata,
            'contract_address_salt': transaction.contract_address_salt,
            'transaction_hash': transaction.transaction_hash,
            'transaction_type': transaction.transaction_type,
            'version': transaction.version,
            'calldata': transaction.calldata,
            'contract_address': transaction.contract_address,
            'entry_point_selector': transaction.entry_point_selector,
            'max_fee': transaction.max_fee,
            'nonce': transaction.nonce,
            'signature': transaction.signature,
            'sender_address': transaction.sender_address
        }
