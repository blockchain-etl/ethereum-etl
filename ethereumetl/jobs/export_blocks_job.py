import json

from ethereumetl.jobs.batch_export_job import BatchExportJob
from ethereumetl.json_rpc_requests import generate_get_block_by_number_json_rpc
from ethereumetl.mappers.block_mapper import EthBlockMapper
from ethereumetl.mappers.transaction_mapper import EthTransactionMapper


# Exports blocks and transactions
class ExportBlocksJob(BatchExportJob):
    def __init__(
            self,
            start_block,
            end_block,
            batch_size,
            ipc_wrapper,
            max_workers,
            item_exporter,
            export_blocks=True,
            export_transactions=True):
        super().__init__(start_block, end_block, batch_size, max_workers)
        self.ipc_wrapper = ipc_wrapper

        self.item_exporter = item_exporter

        self.export_blocks = export_blocks
        self.export_transactions = export_transactions
        if not self.export_blocks and not self.export_transactions:
            raise ValueError('Either blocks_output or transactions_output must be provided')

        self.block_mapper = EthBlockMapper()
        self.transaction_mapper = EthTransactionMapper()

    def _start(self):
        super()._start()
        self.item_exporter.open()

    def _export_batch(self, batch_start, batch_end):
        blocks_rpc = list(generate_get_block_by_number_json_rpc(batch_start, batch_end, self.export_transactions))
        response = self.ipc_wrapper.make_request(json.dumps(blocks_rpc))
        for response_item in response:
            result = response_item['result']
            block = self.block_mapper.json_dict_to_block(result)
            self._export_block(block)

    def _export_block(self, block):
        if self.export_blocks:
            self.item_exporter.export_item(self.block_mapper.block_to_dict(block))
        if self.export_transactions:
            for tx in block.transactions:
                self.item_exporter.export_item(self.transaction_mapper.transaction_to_dict(tx))

    def _end(self):
        super()._end()
        self.item_exporter.close()
