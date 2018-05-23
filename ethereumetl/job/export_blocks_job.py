import json

from web3.utils.threads import Timeout

from ethereumetl.executor.bounded_executor import BoundedExecutor
from ethereumetl.executor.fail_safe_executor import FailSafeExecutor
from ethereumetl.exporters import CsvItemExporter
from ethereumetl.file_utils import get_file_handle, close_silently
from ethereumetl.job.base_job import BaseJob
from ethereumetl.json_rpc_requests import generate_get_block_by_number_json_rpc
from ethereumetl.mapper.block_mapper import EthBlockMapper
from ethereumetl.mapper.transaction_mapper import EthTransactionMapper
from ethereumetl.utils import split_to_batches

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


# Exports blocks and transactions
class ExportBlocksJob(BaseJob):
    def __init__(
            self,
            start_block,
            end_block,
            batch_size,
            ipc_wrapper,
            max_workers=5,
            max_queue=5,
            blocks_output=None,
            transactions_output=None):
        self.start_block = start_block
        self.end_block = end_block
        self.batch_size = batch_size
        self.ipc_wrapper = ipc_wrapper
        self.max_workers = max_workers
        self.max_queue = max_queue
        self.blocks_output = blocks_output
        self.transactions_output = transactions_output

        self.export_blocks = blocks_output is not None
        self.export_transactions = transactions_output is not None
        if not self.export_blocks and not self.export_transactions:
            raise ValueError('Either blocks_output or transactions_output must be provided')

        self.block_mapper = EthBlockMapper()
        self.transaction_mapper = EthTransactionMapper()

        self.blocks_output_file = None
        self.transactions_output_file = None

        self.blocks_exporter = None
        self.transactions_exporter = None

        self.executor: FailSafeExecutor = None

    def _start(self):
        # Using bounded executor prevents unlimited queue growth
        # and allows monitoring in-progress futures and failing fast in case of errors.
        self.executor = FailSafeExecutor(BoundedExecutor(self.max_queue, self.max_workers))

        self.blocks_output_file = get_file_handle(self.blocks_output, binary=True)
        self.blocks_exporter = CsvItemExporter(
            self.blocks_output_file, fields_to_export=BLOCK_FIELDS_TO_EXPORT)

        self.transactions_output_file = get_file_handle(self.transactions_output, binary=True)
        self.transactions_exporter = CsvItemExporter(
            self.transactions_output_file, fields_to_export=TRANSACTION_FIELDS_TO_EXPORT)

    def _export(self):
        for batch_start, batch_end in split_to_batches(self.start_block, self.end_block, self.batch_size):
            self.executor.submit(self._fail_safe_export_batch, batch_start, batch_end)

    def _fail_safe_export_batch(self, batch_start, batch_end):
        try:
            self._export_batch(batch_start, batch_end)
        except (Timeout, OSError):
            # try exporting blocks one by one
            for block_number in range(batch_start, batch_end + 1):
                self._export_batch(block_number, block_number)

    def _export_batch(self, batch_start, batch_end):
        blocks_rpc = list(generate_get_block_by_number_json_rpc(batch_start, batch_end, self.export_transactions))
        response = self.ipc_wrapper.make_request(json.dumps(blocks_rpc))
        for response_item in response:
            result = response_item['result']
            block = self.block_mapper.json_dict_to_block(result)
            self._export_block(block)

    def _export_block(self, block):
        if self.export_blocks:
            self.blocks_exporter.export_item(self.block_mapper.block_to_dict(block))
        if self.export_transactions:
            for tx in block.transactions:
                self.transactions_exporter.export_item(self.transaction_mapper.transaction_to_dict(tx))

    def _end(self):
        self.executor.shutdown()
        close_silently(self.blocks_output_file)
        close_silently(self.transactions_output_file)
