import json

from web3.utils.threads import Timeout

from ethereumetl.bounded_executor import BoundedExecutor
from ethereumetl.exporters import CsvItemExporter
from ethereumetl.file_utils import get_file_handle, close_silently
from ethereumetl.job.base_job import BaseJob
from ethereumetl.json_rpc_requests import generate_get_block_by_number_json_rpc
from ethereumetl.mapper.block_mapper import EthBlockMapper
from ethereumetl.mapper.transaction_mapper import EthTransactionMapper
from ethereumetl.utils import split_to_batches


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

        self.executor = None
        self.futures = []

    def _start(self):
        # Using bounded executor prevents unlimited queue growth
        # and allows monitoring in-progress futures and failing fast in case of errors.
        self.executor = BoundedExecutor(self.max_queue, self.max_workers)

        self.blocks_output_file = get_file_handle(self.blocks_output, binary=True)
        self.transactions_output_file = get_file_handle(self.transactions_output, binary=True)

        self.blocks_exporter = CsvItemExporter(self.blocks_output_file)
        self.transactions_exporter = CsvItemExporter(self.transactions_output_file)

    def _export(self):
        for batch_start, batch_end in split_to_batches(self.start_block, self.end_block, self.batch_size):
            future = self.executor.submit(self._export_batch_with_retries, batch_start, batch_end)
            self.futures.append(future)
            self._check_completed_futures()

    def _export_batch_with_retries(self, batch_start, batch_end):
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

    def _check_completed_futures(self):
        for future in self.futures.copy():
            if future.done():
                # Will throw an exception here if the future failed
                future.result()
                self.futures.remove(future)

    def _export_block(self, block):
        if self.export_blocks:
            self.blocks_exporter.export_item(self.block_mapper.block_to_dict(block))
        if self.export_transactions:
            for tx in block.transactions:
                self.transactions_exporter.export_item(self.transaction_mapper.transaction_to_dict(tx))

    def _end(self):
        self.executor.shutdown(wait=True)
        self._check_completed_futures()
        assert len(self.futures) == 0
        close_silently(self.blocks_output_file)
        close_silently(self.transactions_output_file)
