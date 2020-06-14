class OriginMarketplaceListingMapper(object):
    def listing_to_dict(self, listing):
        return {
            'type': 'origin_marketplace_listing',
            'listing_id': listing.listing_id,
            'ipfs_hash': listing.ipfs_hash,
            'listing_type': listing.listing_type,
            'category': listing.category,
            'subcategory': listing.subcategory,
            'language': listing.language,
            'title': listing.title,
            'description': listing.description,
            'price': listing.price,
            'currency': listing.currency,
            'block_number': listing.block_number,
            'log_index': listing.log_index
        }

class OriginShopProductMapper(object):
    def product_to_dict(self, product):
        return {
            'type': 'origin_shop_product',
            'listing_id': product.listing_id,
            'product_id': product.product_id,
            'ipfs_path': product.ipfs_path,
            'external_id': product.external_id,
            'parent_external_id': product.parent_external_id,
            'title': product.title,
            'description': product.description,
            'price': product.price,
            'currency': product.currency,
            'option1': product.option1,
            'option2': product.option2,
            'option3': product.option3,
            'image': product.image,
            'block_number': product.block_number,
            'log_index': product.log_index
        }
