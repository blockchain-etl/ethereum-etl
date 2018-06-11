import logging
from builtins import map

from ethereumetl.domain.erc20_transfer import EthErc20Transfer
from ethereumetl.utils import chunk_string, hex_to_dec, to_normalized_address

# https://ethereum.stackexchange.com/questions/12553/understanding-logs-and-log-blooms
TRANSFER_EVENT_TOPIC = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
logger = logging.getLogger(__name__)


class EthErc20Processor(object):
    def filter_transfer_from_log(self, receipt_log):

        topics = receipt_log.topics
        if len(topics) < 1:
            logger.warning("Topics are empty in log {} of transaction {}".format(receipt_log.log_index,
                                                                                 receipt_log.transaction_hash))
            return None

        if topics[0] == TRANSFER_EVENT_TOPIC:
            # Handle unindexed event fields
            topics_with_data = topics + split_to_words(receipt_log.data)
            # if the number of topics and fields in data part != 4, then it's a weird event
            if len(topics_with_data) != 4:
                logger.warning("The number of topics and data parts is not equal to 4 in log {} of transaction {}"
                               .format(receipt_log.log_index, receipt_log.transaction_hash))
                return None

            erc20_transfer = EthErc20Transfer()
            erc20_transfer.erc20_token = to_normalized_address(receipt_log.address)
            erc20_transfer.erc20_from = word_to_address(topics_with_data[1])
            erc20_transfer.erc20_to = word_to_address(topics_with_data[2])
            erc20_transfer.erc20_value = hex_to_dec(topics_with_data[3])
            erc20_transfer.erc20_tx_hash = receipt_log.transaction_hash
            erc20_transfer.erc20_log_index = receipt_log.log_index
            erc20_transfer.erc20_block_number = receipt_log.block_number
            return erc20_transfer

        return None


def split_to_words(data):
    if data and len(data) > 2:
        data_without_0x = data[2:]
        words = list(chunk_string(data_without_0x, 64))
        words_with_0x = list(map(lambda word: '0x' + word, words))
        return words_with_0x
    return []


def word_to_address(param):
    if param is None:
        return None
    elif len(param) >= 40:
        return to_normalized_address('0x' + param[-40:])
    else:
        return to_normalized_address(param)
