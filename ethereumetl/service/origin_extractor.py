import base58
import logging

from ethereumetl.utils import hex_to_dec, to_normalized_address
from ethereumetl.ipfs.origin import get_origin_marketplace_data

#
LISTING_CREATED_TOPIC = '0xec3d306143145322b45d2788d826e3b7b9ad062f16e1ec59a5eaba214f96ee3c'
LISTING_UPDATED_TOPIC = '0x470503ad37642fff73a57bac35e69733b6b38281a893f39b50c285aad1f040e0'
PROCESSABLE_TOPICS = [LISTING_CREATED_TOPIC, LISTING_UPDATED_TOPIC]

TOPICS_LEN = 2

logger = logging.getLogger(__name__)


# Helper function. Converts a bytes32 hex string to a base58 encoded ipfs hash.
# For example:
#   "0x017dfd85d4f6cb4dcd715a88101f7b1f06cd1e009b2327a0809d01eb9c91f231"
#   --> "QmNSUYVKDSvPUnRLKmuxk9diJ6yS96r1TrAXzjTiBcCLAL"
def hex_to_ipfs_hash(param):
    data = bytearray.fromhex('1220' + param[2:])
    return base58.b58encode(data).decode()


# Helper function. Composes an Origin Protocol fully-qualified listing id.
# Its format is "<ethereum_network_id>-<contract_version>-<marketplace_listing_id>"
# For example:
#   "1-001-272" refers to listing 272 on marketplace contract version 1, on Mainnet.
def compose_listing_id(network_id, contract_version, listing_id):
    return "{}-{}-{}".format(network_id, contract_version, listing_id)


class OriginEventExtractor(object):
    def __init__(self, ipfs_client):
        self.ipfs_client = ipfs_client

    def extract_event_from_log(self, receipt_log, contract_version):
        topics = receipt_log.topics
        if (topics is None) or (len(topics) == 0):
            logger.warning("Empty topics in log {} of transaction {}".format(
                receipt_log.log_index, receipt_log.transaction_hash))
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

        listing_id = hex_to_dec(topics[2])
        ipfs_hash = hex_to_ipfs_hash(receipt_log.data)

        full_listing_id = compose_listing_id(1, contract_version, listing_id)
        marketplace_listing, shop_products = get_origin_marketplace_data(receipt_log, full_listing_id, self.ipfs_client, ipfs_hash)

        return marketplace_listing, shop_products
