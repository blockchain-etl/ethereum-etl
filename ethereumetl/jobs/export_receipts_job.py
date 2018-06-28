import json

from ethereumetl.jobs.base_job import BaseJob
from ethereumetl.executors.batch_work_executor import BatchWorkExecutor
from ethereumetl.json_rpc_requests import generate_get_receipt_by_tx_hash_json_rpc
from ethereumetl.mappers.receipt_log_mapper import EthReceiptLogMapper
from ethereumetl.mappers.receipt_mapper import EthReceiptMapper
from ethereumetl.utils import rpc_response_batch_to_results


# Exports receipts and logs
class ExportReceiptsJob(BaseJob):
    def __init__(
            self,
            tx_hashes_iterator,
            batch_size,
            ipc_wrapper,
            max_workers,
            item_exporter,
            export_receipts=True,
            export_logs=True):
        self.ipc_wrapper = ipc_wrapper
        self.tx_hashes_iterator = tx_hashes_iterator

        self.batch_work_executor = BatchWorkExecutor(batch_size, max_workers)
        self.item_exporter = item_exporter

        self.export_receipts = export_receipts
        self.export_logs = export_logs
        if not self.export_receipts and not self.export_logs:
            raise ValueError('At least one of export_receipts  or export_logs must be True')

        self.receipt_mapper = EthReceiptMapper()
        self.receipt_log_mapper = EthReceiptLogMapper()

    def _start(self):
        self.item_exporter.open()
        self.batch_work_executor.start()

    def _export(self):
        self.batch_work_executor.execute(self.tx_hashes_iterator, self._export_receipts)

    def _export_receipts(self, tx_hashes):
        receipts_rpc = list(generate_get_receipt_by_tx_hash_json_rpc(tx_hashes))
        response = self.ipc_wrapper.make_request(json.dumps(receipts_rpc))
        results = rpc_response_batch_to_results(response)
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
        self.batch_work_executor.end()
        self.item_exporter.close()
