from ethscraper.domain.transaction_receipt_log import EthTransactionReceiptLog
from ethscraper.utils import hex_to_dec


class EthTransactionReceiptLogMapper(object):

    def json_dict_to_transaction_receipt_log(self, json_dict):
        # type: ({}) -> EthTransactionReceiptLog

        tx_receipt_log = EthTransactionReceiptLog()

        tx_receipt_log.log_index = hex_to_dec(json_dict.get('logIndex', None))
        tx_receipt_log.transaction_hash = json_dict.get('transactionHash', None)
        tx_receipt_log.block_hash = json_dict.get('blockHash', None)
        tx_receipt_log.block_number = hex_to_dec(json_dict.get('blockNumber', None))
        tx_receipt_log.address = json_dict.get('address', None)
        tx_receipt_log.data = json_dict.get('data', None)
        tx_receipt_log.topics = json_dict.get('topics', None)

        return tx_receipt_log


