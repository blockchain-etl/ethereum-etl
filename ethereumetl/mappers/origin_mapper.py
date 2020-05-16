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

class OriginShopListingMapper(object):
    def listing_to_dict(self, listing):
        return {
            'type': 'origin_shop_listing',
            'shop_id': listing.shop_id,
            'product_id': listing.product_id,
            'ipfs_path': listing.ipfs_path,
            'external_id': listing.external_id,
            'parent_external_id': listing.parent_external_id,
            'title': listing.title,
            'description': listing.description,
            'price': listing.price,
            'option1': listing.option1,
            'option2': listing.option2,
            'option3': listing.option3,
            'image': listing.image,
            'block_number': listing.block_number,
            'log_index': listing.log_index
        }
