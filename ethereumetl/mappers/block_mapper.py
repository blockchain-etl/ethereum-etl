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
        block.number = hex_to_dec(json_dict.get('number', None))
        block.hash = json_dict.get('hash', None)
        block.parent_hash = json_dict.get('parentHash', None)
        block.nonce = json_dict.get('nonce', None)
        block.sha3_uncles = json_dict.get('sha3Uncles', None)
        block.logs_bloom = json_dict.get('logsBloom', None)
        block.transactions_root = json_dict.get('transactionsRoot', None)
        block.state_root = json_dict.get('stateRoot', None)
        block.miner = to_normalized_address(json_dict.get('miner', None))
        block.difficulty = hex_to_dec(json_dict.get('difficulty', None))
        block.total_difficulty = hex_to_dec(json_dict.get('totalDifficulty', None))
        block.size = hex_to_dec(json_dict.get('size', None))
        block.extra_data = json_dict.get('extraData', None)
        block.gas_limit = hex_to_dec(json_dict.get('gasLimit', None))
        block.gas_used = hex_to_dec(json_dict.get('gasUsed', None))
        block.timestamp = hex_to_dec(json_dict.get('timestamp', None))

        if 'transactions' in json_dict:
            block.transactions = [
                self.transaction_mapper.json_dict_to_transaction(tx) for tx in json_dict['transactions']
                if isinstance(tx, dict)
            ]

            block.transaction_count = len(json_dict['transactions'])

        return block

    def block_to_dict(self, block):
        return {
            'type': 'block',
            'number': block.number,
            'hash': block.hash,
            'parent_hash': block.parent_hash,
            'nonce': block.nonce,
            'sha3_uncles': block.sha3_uncles,
            'logs_bloom': block.logs_bloom,
            'transactions_root': block.transactions_root,
            'state_root': block.state_root,
            'miner': block.miner,
            'difficulty': block.difficulty,
            'total_difficulty': block.total_difficulty,
            'size': block.size,
            'extra_data': block.extra_data,
            'gas_limit': block.gas_limit,
            'gas_used': block.gas_used,
            'timestamp': block.timestamp,
            'transaction_count': block.transaction_count,
        }
