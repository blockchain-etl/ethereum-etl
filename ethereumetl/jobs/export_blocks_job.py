import json

from ethereumetl.jobs.batch_export_job import BatchExportJob
from ethereumetl.json_rpc_requests import generate_get_block_by_number_json_rpc, \
    generate_get_receipt_by_tx_hash_json_rpc
from ethereumetl.mappers.block_mapper import EthBlockMapper
from ethereumetl.mappers.receipt_log_mapper import EthReceiptLogMapper
from ethereumetl.mappers.receipt_mapper import EthReceiptMapper
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
            export_transactions=True,
            export_receipts=False,
            export_logs=False):
        super().__init__(start_block, end_block, batch_size, max_workers)
        self.ipc_wrapper = ipc_wrapper

        self.item_exporter = item_exporter

        self.export_blocks = export_blocks
        self.export_transactions = export_transactions
        self.export_receipts = export_receipts
        self.export_logs = export_logs
        if not self.export_blocks and not self.export_transactions and not self.export_receipts and not self.export_logs:
            raise ValueError('At least one of export_blocks or export_transactions or ' +
                             'export_receipts  or export_logs must be True')

        self.block_mapper = EthBlockMapper()
        self.transaction_mapper = EthTransactionMapper()
        self.receipt_mapper = EthReceiptMapper()
        self.receipt_log_mapper = EthReceiptLogMapper()

    def _start(self):
        super()._start()
        self.item_exporter.open()

    def _export_batch(self, batch_start, batch_end):
        blocks_rpc = list(generate_get_block_by_number_json_rpc(batch_start, batch_end, self.export_transactions))
        response = self.ipc_wrapper.make_request(json.dumps(blocks_rpc))
        results = self._batch_rpc_response_to_results(response)
        blocks = [self.block_mapper.json_dict_to_block(result) for result in results]

        for block in blocks:
            self._export_block(block)

        # Refactor this when receipts are added to blocks rpc https://github.com/ethereum/go-ethereum/issues/17044
        if self.export_receipts:
            tx_hashes = [tx.hash for block in blocks for tx in block.transactions]
            self._export_receipts(tx_hashes)

    def _batch_rpc_response_to_results(self, response):
        for response_item in response:
            yield response_item['result']

    def _export_block(self, block):
        if self.export_blocks:
            self.item_exporter.export_item(self.block_mapper.block_to_dict(block))
        if self.export_transactions:
            for tx in block.transactions:
                self.item_exporter.export_item(self.transaction_mapper.transaction_to_dict(tx))

    def _export_receipts(self, tx_hashes):
        if len(tx_hashes) == 0:
            return

        receipts_rpc = list(generate_get_receipt_by_tx_hash_json_rpc(tx_hashes))
        response = self.ipc_wrapper.make_request(json.dumps(receipts_rpc))
        results = self._batch_rpc_response_to_results(response)
        receipts = [self.receipt_mapper.json_dict_to_receipt(result) for result in results]
        for receipt in receipts:
            self._export_receipt(receipt)

    def _export_receipt(self, receipt):
        if self.export_receipts:
            self.item_exporter.export_item(self.receipt_mapper.receipt_to_dict(receipt))
            if self.export_logs:
                for log in receipt.logs:
                    self.item_exporter.export_item(self.receipt_log_mapper.receipt_log_to_dict(log))

    def _end(self):
        super()._end()
        self.item_exporter.close()
