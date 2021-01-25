class OriginMarketplaceListing(object):
    def __init__(self):
        self.listing_id = None
        self.ipfs_hash = None
        self.listing_type = None
        self.category = None
        self.subcategory = None
        self.language = None
        self.title = None
        self.description = None
        self.price = None
        self.currency = None
        self.block_number = None
        self.log_index = None

class OriginShopProduct(object):
    def __init__(self):
        self.listing_id = None
        self.product_id = None
        self.ipfs_path = None
        self.external_id = None
        self.parent_external_id = None
        self.title = None
        self.description = None
        self.price = None
        self.currency = None
        self.image = None
        self.option1 = None
        self.option2 = None
        self.option3 = None
        self.block_number = None
        self.log_index = None
