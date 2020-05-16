from blockchainetl.jobs.exporters.composite_item_exporter import CompositeItemExporter

MARKETPLACE_FIELDS_TO_EXPORT = [
    'block_number',
    'log_index',
    'listing_id',
    'ipfs_hash',
    'listing_type',
    'ipfs_hash',
    'category',
    'subcategory',
    'language',
    'title',
    'description',
    'price',
    'currency'
]

SHOP_FIELDS_TO_EXPORT = [
    'block_number',
    'log_index',
    'shop_id',
    'product_id',
    'ipfs_path',
    'ipfs_hash',
    'external_id',
    'parent_external_id',
    'title',
    'description',
    'price',
    'option1',
    'option2',
    'option3',
    'image'
]

def origin_marketplace_listing_item_exporter(output):
    return CompositeItemExporter(
        filename_mapping={
            'origin_marketplace_listing': output
        },
        field_mapping={
            'origin_marketplace_listing': MARKETPLACE_FIELDS_TO_EXPORT
        }
    )

def origin_shop_listing_item_exporter(output):
    return CompositeItemExporter(
        filename_mapping={
            'origin_shop_listing': output
        },
        field_mapping={
            'origin_shop_listing': SHOP_FIELDS_TO_EXPORT
        }
    )


