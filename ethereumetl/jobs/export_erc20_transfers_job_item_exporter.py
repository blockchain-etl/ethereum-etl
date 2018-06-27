from ethereumetl.jobs.composite_item_exporter import CompositeItemExporter

FIELDS_TO_EXPORT = [
    'erc20_token',
    'erc20_from',
    'erc20_to',
    'erc20_value',
    'erc20_tx_hash',
    'erc20_log_index',
    'erc20_block_number'
]


def export_erc20_transfers_job_item_exporter(erc20_transfer_output):
    return CompositeItemExporter(
        filename_mapping={
            'erc20_transfer': erc20_transfer_output
        },
        field_mapping={
            'erc20_transfer': FIELDS_TO_EXPORT
        }
    )
