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

        receipt.transaction_hash = json_dict.get('transactionHash', None)
        receipt.transaction_index = hex_to_dec(json_dict.get('transactionIndex', None))
        receipt.block_hash = json_dict.get('blockHash', None)
        receipt.block_number = hex_to_dec(json_dict.get('blockNumber', None))
        receipt.from_address = to_normalized_address(json_dict.get('from', None))
        receipt.to_address = to_normalized_address(json_dict.get('to', None))
        receipt.cumulative_gas_used = hex_to_dec(json_dict.get('cumulativeGasUsed', None))
        receipt.gas_used = hex_to_dec(json_dict.get('gasUsed', None))

        receipt.contract_address = to_normalized_address(json_dict.get('contractAddress', None))

        receipt.root = json_dict.get('root', None)
        receipt.status = hex_to_dec(json_dict.get('status', None))

        if 'logs' in json_dict:
            receipt.logs = [
                self.receipt_log_mapper.json_dict_to_receipt_log(log) for log in json_dict['logs']
            ]

        return receipt

    def receipt_to_dict(self, receipt):
        return {
            'type': 'receipt',
            'receipt_transaction_hash': receipt.transaction_hash,
            'receipt_transaction_index': receipt.transaction_index,
            'receipt_block_hash': receipt.block_hash,
            'receipt_block_number': receipt.block_number,
            'receipt_from_address': receipt.from_address,
            'receipt_to_address': receipt.to_address,
            'receipt_cumulative_gas_used': receipt.cumulative_gas_used,
            'receipt_gas_used': receipt.gas_used,
            'receipt_contract_address': receipt.contract_address,
            'receipt_root': receipt.root,
            'receipt_status': receipt.status
        }
