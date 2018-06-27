from ethereumetl.exporters import CsvItemExporter
from ethereumetl.file_utils import get_file_handle, close_silently

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


class ExportBlocksJobItemExporter:
    def __init__(
            self,
            blocks_output=None,
            transactions_output=None,
            block_fields_to_export=BLOCK_FIELDS_TO_EXPORT,
            transaction_fields_to_export=TRANSACTION_FIELDS_TO_EXPORT):
        self.blocks_output = blocks_output
        self.transactions_output = transactions_output
        self.block_fields_to_export = block_fields_to_export
        self.transaction_fields_to_export = transaction_fields_to_export

        self.export_blocks = blocks_output is not None
        self.export_transactions = transactions_output is not None

        self.blocks_output_file = None
        self.transactions_output_file = None

        self.blocks_exporter = None
        self.transactions_exporter = None

    def open(self):
        self.blocks_output_file = get_file_handle(self.blocks_output, binary=True, create_parent_dirs=True)
        self.blocks_exporter = CsvItemExporter(
            self.blocks_output_file, fields_to_export=self.block_fields_to_export)

        self.transactions_output_file = get_file_handle(self.transactions_output, binary=True, create_parent_dirs=True)
        self.transactions_exporter = CsvItemExporter(
            self.transactions_output_file, fields_to_export=self.transaction_fields_to_export)

    def export_item(self, item):
        item_type = item.get('type', None)
        if item_type == 'block':
            self.blocks_exporter.export_item(item)
        elif item_type == 'transaction':
            self.transactions_exporter.export_item(item)
        else:
            raise ValueError('Unknown item time {}'.format(item_type))

    def close(self):
        close_silently(self.blocks_output_file)
        close_silently(self.transactions_output_file)
