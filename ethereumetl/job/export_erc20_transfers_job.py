from web3.utils.threads import Timeout

from ethereumetl.executor.bounded_executor import BoundedExecutor
from ethereumetl.executor.fail_safe_executor import FailSafeExecutor
from ethereumetl.exporters import CsvItemExporter
from ethereumetl.file_utils import get_file_handle, close_silently
from ethereumetl.job.base_job import BaseJob
from ethereumetl.mapper.erc20_transfer_mapper import EthErc20TransferMapper
from ethereumetl.mapper.receipt_log_mapper import EthReceiptLogMapper
from ethereumetl.service.erc20_processor import EthErc20Processor, TRANSFER_EVENT_TOPIC
from ethereumetl.utils import split_to_batches

FIELDS_TO_EXPORT = [
    'erc20_token',
    'erc20_from',
    'erc20_to',
    'erc20_value',
    'erc20_tx_hash',
    'erc20_block_number'
]


class ExportErc20TransfersJob(BaseJob):
    def __init__(
            self,
            start_block,
            end_block,
            batch_size,
            web3,
            output,
            max_workers=5,
            tokens=None):
        self.start_block = start_block
        self.end_block = end_block
        self.batch_size = batch_size
        self.web3 = web3
        self.output = output
        self.max_workers = max_workers
        self.tokens = tokens

        self.receipt_log_mapper = EthReceiptLogMapper()
        self.erc20_transfer_mapper = EthErc20TransferMapper()
        self.erc20_processor = EthErc20Processor()

        self.output_file = None
        self.exporter = None

        self.executor: FailSafeExecutor = None

    def _start(self):
        # Using bounded executor prevents unlimited queue growth
        # and allows monitoring in-progress futures and failing fast in case of errors.
        self.executor = FailSafeExecutor(BoundedExecutor(1, self.max_workers))

        self.output_file = get_file_handle(self.output, binary=True)
        self.exporter = CsvItemExporter(self.output_file, fields_to_export=FIELDS_TO_EXPORT)

    def _export(self):
        for batch_start, batch_end in split_to_batches(self.start_block, self.end_block, self.batch_size):
            self.executor.submit(self._fail_safe_export_batch, batch_start, batch_end)

    def _fail_safe_export_batch(self, batch_start, batch_end):
        try:
            self._export_batch(batch_start, batch_end)
        except (Timeout, OSError):
            # try exporting one by one
            for block_number in range(batch_start, batch_end + 1):
                self._export_batch(block_number, block_number)

    def _export_batch(self, batch_start, batch_end):
        filter_params = {
            'fromBlock': batch_start,
            'toBlock': batch_end,
            'topics': [TRANSFER_EVENT_TOPIC]
        }

        if self.tokens is not None and len(self.tokens) > 0:
            filter_params['address'] = self.tokens

        event_filter = self.web3.eth.filter(filter_params)
        events = event_filter.get_all_entries()
        for event in events:
            log = self.receipt_log_mapper.web3_dict_to_receipt_log(event)
            erc20_transfer = self.erc20_processor.filter_transfer_from_log(log)
            if erc20_transfer is not None:
                self.exporter.export_item(self.erc20_transfer_mapper.erc20_transfer_to_dict(erc20_transfer))

        self.web3.eth.uninstallFilter(event_filter.filter_id)

    def _end(self):
        self.executor.shutdown()
        close_silently(self.output_file)
