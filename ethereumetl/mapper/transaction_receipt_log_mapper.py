from ethereumetl.domain.transaction_receipt_log import EthTransactionReceiptLog
from ethereumetl.utils import hex_to_dec


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

    def web3_dict_to_transaction_receipt_log(self, dict):
        # type: ({}) -> EthTransactionReceiptLog

        tx_receipt_log = EthTransactionReceiptLog()

        tx_receipt_log.log_index = dict.get('logIndex', None)

        transaction_hash = dict.get('transactionHash', None)
        if transaction_hash is not None:
            transaction_hash = transaction_hash.hex()
        tx_receipt_log.transaction_hash = transaction_hash

        block_hash = dict.get('blockHash', None)
        if block_hash is not None:
            block_hash = block_hash.hex()
        tx_receipt_log.block_hash = block_hash

        tx_receipt_log.block_number = dict.get('blockNumber', None)
        tx_receipt_log.address = dict.get('address', None)
        tx_receipt_log.data = dict.get('data', None)

        if 'topics' in dict:
            tx_receipt_log.topics = list(map(lambda topic: topic.hex(), dict['topics']))

        return tx_receipt_log
