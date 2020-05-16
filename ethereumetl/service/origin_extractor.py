import base58
import logging

from ethereumetl.utils import hex_to_dec, to_normalized_address
from ethereumetl.ipfs.origin import get_origin_marketplace_data

LISTING_CREATED_TOPIC = '0xec3d306143145322b45d2788d826e3b7b9ad062f16e1ec59a5eaba214f96ee3c'
LISTING_UPDATED_TOPIC = '0x470503ad37642fff73a57bac35e69733b6b38281a893f39b50c285aad1f040e0'
PROCESSABLE_TOPICS = [LISTING_CREATED_TOPIC, LISTING_UPDATED_TOPIC]

TOPICS_LEN = 2

logger = logging.getLogger(__name__)


class OriginEventExtractor(object):
    def extract_event_from_log(self, receipt_log):
        topics = receipt_log.topics
        if (topics is None) or (len(topics) == 0):
            logger.warning("Empty topics in log {} of transaction {}".format(receipt_log.log_index,
                                                                                 receipt_log.transaction_hash))
            return None, []

        topic = topics[0]
        if topic not in PROCESSABLE_TOPICS:
            logger.debug("Skip processing event with signature {}".format(topic))
            return None, []

        if len(topics) < TOPICS_LEN:
            logger.warning("Unexpected number of topics {} in log {} of transaction {}".format(
                len(topics),
                receipt_log.log_index,
                receipt_log.transaction_hash))
            return None, []


        contract_address = to_normalized_address(receipt_log.address)
        party = word_to_address(topics[1])
        listing_id = hex_to_dec(topics[2])
        ipfs_hash = hex_to_ipfs_hash(receipt_log.data)

        marketplace_listing, shop_listings = get_origin_marketplace_data(receipt_log, listing_id, ipfs_hash)

        return marketplace_listing, shop_listings


def word_to_address(param):
    if param is None:
        return None
    elif len(param) >= 40:
        return to_normalized_address('0x' + param[-40:])
    else:
        return to_normalized_address(param)


# Return base58 encoded ipfs hash from bytes32 hex string,
# For ex. "0x017dfd85d4f6cb4dcd715a88101f7b1f06cd1e009b2327a0809d01eb9c91f231"
# --> "QmNSUYVKDSvPUnRLKmuxk9diJ6yS96r1TrAXzjTiBcCLAL"
def hex_to_ipfs_hash(param):
    data = bytearray.fromhex('1220' + param[2:])
    return base58.b58encode(data).decode()
