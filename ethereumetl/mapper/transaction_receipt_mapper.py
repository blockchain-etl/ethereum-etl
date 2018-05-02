from ethscraper.domain.transaction_receipt import EthTransactionReceipt
from ethscraper.mapper.transaction_receipt_log_mapper import EthTransactionReceiptLogMapper
from ethscraper.utils import hex_to_dec
from builtins import map


class EthTransactionReceiptMapper(object):
    transaction_receipt_log_mapper = EthTransactionReceiptLogMapper()

    def json_dict_to_transaction_receipt(self, json_dict):
        # type: ({}) -> EthTransactionReceipt

        receipt = EthTransactionReceipt()

        receipt.transaction_hash = json_dict.get('transactionHash', None)
        receipt.transaction_index = hex_to_dec(json_dict.get('transactionIndex', None))
        receipt.block_number = hex_to_dec(json_dict.get('blockNumber', None))
        receipt.block_hash = json_dict.get('blockHash', None)
        receipt.cumulative_gas_used = hex_to_dec(json_dict.get('cumulativeGasUsed', None))
        receipt.gas_used = hex_to_dec(json_dict.get('gasUsed', None))

        receipt.contract_address = json_dict.get('contractAddress', None)
        receipt.status = json_dict.get('status', None)

        if 'logs' in json_dict:
            receipt.logs = list(map(
                lambda log: self.transaction_receipt_log_mapper.json_dict_to_transaction_receipt_log(log),
                json_dict['logs']))
        return receipt
