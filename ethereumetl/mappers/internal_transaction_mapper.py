# MIT License
#
# Copyright (c) 2018 Evgeniy Filatov, evgeniyfilatov@gmail.com
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


from ethereumetl.domain.internal_transaction import EthInternalTransaction
from ethereumetl.utils import hex_to_dec, to_normalized_address


class EthInternalTransactionMapper(object):
    def json_dict_to_internal_transaction(self, json_dict):
        transaction = EthInternalTransaction()

        transaction.block_number = json_dict.get('blockNumber', None)
        transaction.hash = json_dict.get('transactionHash', None)
        transaction.trace_id = json_dict.get('traceAddress', [])

        action = json_dict.get('action', {})
        result = json_dict.get('result', {})
        error = json_dict.get('error', {})

        transaction_type = json_dict.get('type', None)

        # common fields in call/create
        if transaction_type in ('call', 'create'):
            transaction.from_address = to_normalized_address(action.get('from', None))
            transaction.value = hex_to_dec(action.get('value', None))
            transaction.gas = hex_to_dec(action.get('gas', None))
            transaction.gas_used = hex_to_dec(result.get('gasUsed', None))

            if error:
                transaction.is_error = True
                transaction.err_code = error
            else:
                transaction.is_error = False

        # differing fields for each transaction type
        if transaction_type == 'call':
            transaction.transaction_type = action.get('callType', None)

            transaction.to_address = to_normalized_address(action.get('to', None))
            transaction.input = action.get('input', None)
        elif transaction_type == 'create':
            transaction.transaction_type = transaction_type

            transaction.to_address = to_normalized_address(0)
            transaction.input = action.get('init', None)
        elif transaction_type == 'suicide':
            transaction.transaction_type = transaction_type

        return transaction

    def internal_transaction_to_dict(self, internal_transaction):
        return {
            'type': 'internal_transaction',
            'block_number': internal_transaction.block_number,
            'block_timestamp': internal_transaction.block_timestamp,
            'hash': internal_transaction.hash,
            'from_address': internal_transaction.from_address,
            'to_address': internal_transaction.to_address,
            'value': internal_transaction.value,
            'contract_address': internal_transaction.contract_address,
            'input': internal_transaction.input,
            'transaction_type': internal_transaction.transaction_type,
            'gas': internal_transaction.gas,
            'gas_used': internal_transaction.gas_used,
            'trace_id': internal_transaction.trace_id,
            'is_error': internal_transaction.is_error,
            'err_code': internal_transaction.err_code,
        }
