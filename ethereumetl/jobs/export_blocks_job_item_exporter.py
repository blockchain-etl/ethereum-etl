from ethereumetl.jobs.composite_item_exporter import CompositeItemExporter

BLOCK_FIELDS_TO_EXPORT = [
    'block_number',
    'block_hash',
    'block_parent_hash',
    'block_nonce',
    'block_sha3_uncles',
    'block_logs_bloom',
    'block_transactions_root',
    'block_state_root',
    'block_miner',
    'block_difficulty',
    'block_total_difficulty',
    'block_size',
    'block_extra_data',
    'block_gas_limit',
    'block_gas_used',
    'block_timestamp',
    'block_transaction_count'
]

TRANSACTION_FIELDS_TO_EXPORT = [
    'tx_hash',
    'tx_nonce',
    'tx_block_hash',
    'tx_block_number',
    'tx_index',
    'tx_from',
    'tx_to',
    'tx_value',
    'tx_gas',
    'tx_gas_price',
    'tx_input'
]


def export_blocks_job_item_exporter(blocks_output=None, transactions_output=None):
    return CompositeItemExporter(
        filename_mapping={
            'block': blocks_output,
            'transaction': transactions_output
        },
        field_mapping={
            'block': BLOCK_FIELDS_TO_EXPORT,
            'transaction': TRANSACTION_FIELDS_TO_EXPORT
        }
    )
