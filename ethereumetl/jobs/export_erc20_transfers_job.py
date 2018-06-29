from ethereumetl.jobs.batch_export_job import BatchExportJob
from ethereumetl.mappers.erc20_transfer_mapper import EthErc20TransferMapper
from ethereumetl.mappers.receipt_log_mapper import EthReceiptLogMapper
from ethereumetl.service.erc20_processor import EthErc20Processor, TRANSFER_EVENT_TOPIC


class ExportErc20TransfersJob(BatchExportJob):
    def __init__(
            self,
            start_block,
            end_block,
            batch_size,
            web3,
            item_exporter,
            max_workers,
            tokens=None):
        super().__init__(start_block, end_block, batch_size, max_workers)
        self.web3 = web3
        self.tokens = tokens
        self.item_exporter = item_exporter

        self.receipt_log_mapper = EthReceiptLogMapper()
        self.erc20_transfer_mapper = EthErc20TransferMapper()
        self.erc20_processor = EthErc20Processor()

    def _start(self):
        super()._start()
        self.item_exporter.open()

    def _export_batch(self, batch_start, batch_end):
        # https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getfilterlogs
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
                self.item_exporter.export_item(self.erc20_transfer_mapper.erc20_transfer_to_dict(erc20_transfer))

        self.web3.eth.uninstallFilter(event_filter.filter_id)

    def _end(self):
        super()._end()
        self.item_exporter.close()
