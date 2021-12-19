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


from ethereumetl.domain.receipt import EthReceipt
from ethereumetl.mappers.receipt_log_mapper import EthReceiptLogMapper
from ethereumetl.utils import hex_to_dec, to_normalized_address


class EthReceiptMapper(object):
    def __init__(self, receipt_log_mapper=None):
        if receipt_log_mapper is None:
            self.receipt_log_mapper = EthReceiptLogMapper()
        else:
            self.receipt_log_mapper = receipt_log_mapper

    def json_dict_to_receipt(self, json_dict):
        receipt = EthReceipt()

        receipt.transaction_hash = json_dict.get('transactionHash')
        receipt.transaction_index = hex_to_dec(json_dict.get('transactionIndex'))
        receipt.block_hash = json_dict.get('blockHash')
        receipt.block_number = hex_to_dec(json_dict.get('blockNumber'))
        receipt.cumulative_gas_used = hex_to_dec(json_dict.get('cumulativeGasUsed'))
        receipt.gas_used = hex_to_dec(json_dict.get('gasUsed'))

        receipt.contract_address = to_normalized_address(json_dict.get('contractAddress'))

        receipt.root = json_dict.get('root')
        receipt.status = hex_to_dec(json_dict.get('status'))

        receipt.effective_gas_price = hex_to_dec(json_dict.get('effectiveGasPrice'))

        if 'logs' in json_dict:
            receipt.logs = [
                self.receipt_log_mapper.json_dict_to_receipt_log(log) for log in json_dict['logs']
            ]

        return receipt

    def receipt_to_dict(self, receipt):
        return {
            'type': 'receipt',
            'transaction_hash': receipt.transaction_hash,
            'transaction_index': receipt.transaction_index,
            'block_hash': receipt.block_hash,
            'block_number': receipt.block_number,
            'cumulative_gas_used': receipt.cumulative_gas_used,
            'gas_used': receipt.gas_used,
            'contract_address': receipt.contract_address,
            'root': receipt.root,
            'status': receipt.status,
            'effective_gas_price': receipt.effective_gas_price
        }
