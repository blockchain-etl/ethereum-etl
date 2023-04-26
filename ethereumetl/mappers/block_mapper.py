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


from ethereumetl.domain.block import EthBlock
from ethereumetl.mappers.transaction_mapper import EthTransactionMapper
from ethereumetl.utils import hex_to_dec, to_normalized_address


class EthBlockMapper(object):
    def __init__(self, transaction_mapper=None):
        if transaction_mapper is None:
            self.transaction_mapper = EthTransactionMapper()
        else:
            self.transaction_mapper = transaction_mapper

    def json_dict_to_block(self, json_dict):
        block = EthBlock()
        block.block_number = json_dict.get('block_number')
        block.block_hash = json_dict.get('block_hash')
        block.new_root = json_dict.get('new_root')
        block.parent_hash = json_dict.get('parent_hash')
        block.sequencer_address = json_dict.get('sequencer_address')
        block.status = json_dict.get('status')
        block.timestamp = json_dict.get('timestamp')

        if 'transactions' in json_dict:
            block.transactions = [
                self.transaction_mapper.json_dict_to_transaction(tx, block_number=block.block_number, block_hash=block.block_hash, block_timestamp=block.timestamp)
                for tx in json_dict['transactions']
                if isinstance(tx, dict)
            ]

            block.transaction_count = len(json_dict['transactions'])

        if 'withdrawals' in json_dict:
            block.withdrawals = self.parse_withdrawals(json_dict['withdrawals'])

        return block

    def parse_withdrawals(self, withdrawals):
        return [
            {
                "index": hex_to_dec(withdrawal["index"]),
                "validator_index": hex_to_dec(withdrawal["validatorIndex"]),
                "address": withdrawal["address"],
                "amount": hex_to_dec(withdrawal["amount"]),
            }
            for withdrawal in withdrawals
        ]

    def block_to_dict(self, block):
        return {
            'type': 'block',
            'block_number': block.block_number,
            'block_hash': block.block_hash,
            'new_root': block.new_root,
            'parent_hash': block.parent_hash,
            'sequencer_address': block.sequencer_address,
            'status': block.status,
            'timestamp': block.timestamp
        }
