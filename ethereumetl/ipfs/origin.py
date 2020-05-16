import ipfsApi
import logging
import re

from ethereumetl.domain.origin import OriginMarketplaceListing, OriginShopListing


logger = logging.getLogger('origin')

IPFS_PRIMARY_HOST = 'ipfs-prod.ogn.app'
IPFS_FALLBACK_HOST = 'gateway.ipfs.io'
IPFS_PORT = 80
IPFS_TIMEOUT = 5  # Timeout in second
IPFS_NUM_ATTEMPTS = 3

ipfs_client1 = ipfsApi.Client(IPFS_PRIMARY_HOST, IPFS_PORT)
ipfs_client2 = ipfsApi.Client(IPFS_PRIMARY_HOST, IPFS_PORT)
ipfs_clients = [ipfs_client1, ipfs_client2]

def _get_ipfs(path):
    for i in range(IPFS_NUM_ATTEMPTS):
        ipfs_client = ipfs_clients[i % 2]
        try:
            data = ipfs_client.cat(path, timeout=IPFS_TIMEOUT)
            return data
        except Exception as e:
            logger.error("Attempt #{} - Failed downloading {}: {}".format(i+1, path, e))
    raise Exception("IPFS download failure for hash {}".format(path))


def _get_ipfs_json(path):
    for i in range(IPFS_NUM_ATTEMPTS):
        ipfs_client = ipfs_clients[i % 2]
        try:
            data = ipfs_client.get_json(path, timeout=IPFS_TIMEOUT)
            return data
        except Exception as e:
            logger.error("Attempt #{} - Failed downloading {}: {}".format(i+1, path, e))
    raise Exception("IPFS download failure for hash {}".format(path))


def _get_shop_data_dir(shop_index_page):
    match = re.search('<link rel="data-dir" href="(.+?)"', shop_index_page)
    return match.group(1) if match else None


# Returns the list of products from the shop.
def _get_origin_shop_listings(receipt_log, listing_id, shop_ipfs_hash):
    # TODO: handle contract v000
    shop_id = '1-001-' + str(listing_id)  # We use the listing_id from the marketplace contract as unique shop_id.

    listings = []
    shop_index_page = _get_ipfs(shop_ipfs_hash + "/index.html")
    shop_data_dir = _get_shop_data_dir(shop_index_page)

    path = "{}/{}".format(shop_ipfs_hash, shop_data_dir) if shop_data_dir else shop_ipfs_hash
    logger.debug("Using shop path {}".format(path))

    # TODO: download the shop config.json and check it references listing_id.

    products_path = "{}/{}".format(path, 'products.json')
    try:
        products = _get_ipfs_json(products_path)
    except Exception as e:
        logger.error("Shop {} Failed downloading shop {}: {}".format(shop_id, products_path, e))
        return listings

    logger.info("Found {} products in for shop {}".format(len(products), shop_id))

    # Go thru all the products from the shop.
    for product in products:
        product_id = product.get('id')
        if not product_id:
            logger.error('Product entry with missing id in products.json')
            continue

        logger.info("Processing product {}".format(product_id))

        # Fetch each product details to get variants.
        product_base_path = "{}/{}".format(path, product_id)
        product_data_path = "{}/{}".format(product_base_path, 'data.json')
        try:
            product = _get_ipfs_json(product_data_path)
        except Exception as e:
            logger.error("Failed downloading {}: {}".format(product_data_path, e))
            continue

        # Index the top product.
        listing = OriginShopListing()
        listing.block_number = receipt_log.block_number
        listing.log_index = receipt_log.log_index
        listing.shop_id = shop_id
        listing.product_id = "{}-{}".format(shop_id, product_id)
        listing.ipfs_path = product_base_path
        listing.external_id = str(product.get('externalId', ''))
        listing.parent_external_id = ''
        listing.title = product.get('title', '')
        listing.description = product.get('description', '')
        listing.price = product.get('price', '')
        listing.option1 = ''
        listing.option2 = ''
        listing.option3 = ''
        listing.image = product.get('image', '')
        listings.append(listing)

        # index the variants, if any
        variants = product.get('variants', [])
        if len(variants) > 0:
            logger.info("Found {} variants".format(len(variants)))
            for variant in variants:
                listing = OriginShopListing()
                listing.block_number = receipt_log.block_number
                listing.log_index = receipt_log.log_index
                listing.shop_id = shop_id
                listing.product_id = "{}-{}".format(shop_id, variant.get('id'))
                listing.ipfs_path = product_base_path
                listing.external_id = str(variant.get('externalId', ''))
                listing.parent_external_id = str(product.get('externalId', ''))
                listing.title = variant.get('title', '')
                listing.description = product.get('description', '')
                listing.price = variant.get('price', '')
                listing.option1 = variant.get('option1', '')
                listing.option2 = variant.get('option2', '')
                listing.option3 = variant.get('option3', '')
                listing.image = variant.get('image', '')
                listings.append(listing)

    return listings

def get_origin_marketplace_data(receipt_log, listing_id, ipfs_hash):
    # Load the listing's metadata from IPFS.
    try:
        listing_data = _get_ipfs_json(ipfs_hash)
    except Exception as e:
        logger.error("Extraction failed. Listing {} Listing hash {} - {}".format(listing_id, ipfs_hash, e))
        return None, []

    listing = OriginMarketplaceListing()
    listing.block_number = receipt_log.block_number
    listing.log_index = receipt_log.log_index
    listing.listing_id = str(listing_id)
    listing.ipfs_hash = ipfs_hash
    listing.listing_type = listing_data.get('listingType', '')
    listing.category = listing_data.get('category', '')
    listing.subcategory =  listing_data.get('subCategory', '')
    listing.language = listing_data.get('language', '')
    listing.title = listing_data.get('title', '')
    listing.description = listing_data.get('description', '')
    listing.price = listing_data.get('price', {}).get('amount', '')
    listing.currency = listing_data.get('price', {}).get('currency', '')
    # TODO: also extract media, commission fields

    # If it is a shop listing, also extract all of the shop data.
    shop_listings = []
    shop_ipfs_hash = listing_data.get('shopIpfsHash')
    if shop_ipfs_hash:
        try:
            shop_listings = _get_origin_shop_listings(receipt_log, listing_id, shop_ipfs_hash)
        except Exception as e:
            logger.error("Extraction failed. Listing {} Shop hash {} - {}".format(listing_id, shop_ipfs_hash, e))

    return listing, shop_listings


