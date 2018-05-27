from ethereumetl.domain.receipt_log import EthReceiptLog


class EthReceiptLogMapper(object):

    def web3_dict_to_receipt_log(self, dict):

        receipt_log = EthReceiptLog()

        receipt_log.log_index = dict.get('logIndex', None)

        transaction_hash = dict.get('transactionHash', None)
        if transaction_hash is not None:
            transaction_hash = transaction_hash.hex()
        receipt_log.transaction_hash = transaction_hash

        block_hash = dict.get('blockHash', None)
        if block_hash is not None:
            block_hash = block_hash.hex()
        receipt_log.block_hash = block_hash

        receipt_log.block_number = dict.get('blockNumber', None)
        receipt_log.address = dict.get('address', None)
        receipt_log.data = dict.get('data', None)

        if 'topics' in dict:
            receipt_log.topics = [topic.hex() for topic in dict['topics']]

        return receipt_log
