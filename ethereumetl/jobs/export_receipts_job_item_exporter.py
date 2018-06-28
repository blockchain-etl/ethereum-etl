from ethereumetl.jobs.composite_item_exporter import CompositeItemExporter

RECEIPT_FIELDS_TO_EXPORT = [
    'receipt_transaction_hash',
    'receipt_transaction_index',
    'receipt_block_hash',
    'receipt_block_number',
    'receipt_cumulative_gas_used',
    'receipt_gas_used',
    'receipt_contract_address',
    'receipt_root',
    'receipt_status'
]

LOG_FIELDS_TO_EXPORT = [
    'log_index',
    'log_transaction_hash',
    'log_transaction_index',
    'log_block_hash',
    'log_block_number',
    'log_address',
    'log_data',
    'log_topics'
]


def export_receipts_job_item_exporter(receipts_output=None, logs_output=None):
    return CompositeItemExporter(
        filename_mapping={
            'receipt': receipts_output,
            'log': logs_output
        },
        field_mapping={
            'receipt': RECEIPT_FIELDS_TO_EXPORT,
            'log': LOG_FIELDS_TO_EXPORT
        }
    )
