import json

from web3.utils.threads import Timeout

from ethereumetl.exporters import CsvItemExporter
from ethereumetl.file_utils import get_file_handle
from ethereumetl.json_rpc_requests import generate_get_block_by_number_json_rpc
from ethereumetl.mapper.block_mapper import EthBlockMapper
from ethereumetl.mapper.transaction_mapper import EthTransactionMapper
from ethereumetl.utils import split_to_batches


class ExportBlocksJob(object):
    def __init__(self,
                 start_block,
                 end_block,
                 batch_size,
                 batch_ipc_provider,
                 blocks_output=None,
                 transactions_output=None):
        self.start_block = start_block
        self.end_block = end_block
        self.batch_size = batch_size
        self.batch_ipc_provider = batch_ipc_provider
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

    def run(self):
        try:
            self._start()
            self._export()
        finally:
            self._end()

    def _start(self):
        self.blocks_output_file = get_file_handle(self.blocks_output, binary=True)
        self.transactions_output_file = get_file_handle(self.transactions_output, binary=True)

        self.blocks_exporter = CsvItemExporter(self.blocks_output_file)
        self.transactions_exporter = CsvItemExporter(self.transactions_output_file)

    def _export(self):
        for batch_start, batch_end in split_to_batches(self.start_block, self.end_block, self.batch_size):
            try:
                self._export_batch(batch_start, batch_end)
            except Timeout:
                # try exporting blocks one by one
                for block_number in range(batch_start, batch_end + 1):
                    self._export_batch(block_number, block_number)

    def _export_batch(self, batch_start, batch_end):
        blocks_rpc = list(generate_get_block_by_number_json_rpc(batch_start, batch_end, self.export_transactions))
        response = self.batch_ipc_provider.make_request(json.dumps(blocks_rpc))
        for response_item in response:
            result = response_item['result']
            block = self.block_mapper.json_dict_to_block(result)
            if self.export_blocks:
                self.blocks_exporter.export_item(self.block_mapper.block_to_dict(block))
            if self.export_transactions:
                for tx in block.transactions:
                    self.transactions_exporter.export_item(self.transaction_mapper.transaction_to_dict(tx))

    def _end(self):
        if self.blocks_output_file is not None:
            self.blocks_output_file.close()
        if self.transactions_output_file is not None:
            self.transactions_output_file.close()
