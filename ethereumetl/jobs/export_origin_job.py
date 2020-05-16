from ethereumetl.executors.batch_work_executor import BatchWorkExecutor
from blockchainetl.jobs.base_job import BaseJob
from ethereumetl.utils import validate_range

from ethereumetl.mappers.receipt_log_mapper import EthReceiptLogMapper
from ethereumetl.mappers.origin_mapper import OriginMarketplaceListingMapper, OriginShopListingMapper
from ethereumetl.service.origin_extractor import OriginEventExtractor


ORIGIN_MARKETPLACE_V1_CONTRACT_ADDRESS = '0x698Ff47B84837d3971118a369c570172EE7e54c2'


class ExportOriginJob(BaseJob):
    def __init__(
            self,
            start_block,
            end_block,
            batch_size,
            web3,
            marketplace_listing_exporter,
            shop_listing_exporter,
            max_workers):
        validate_range(start_block, end_block)
        self.start_block = start_block
        self.end_block = end_block

        self.web3 = web3
        self.contract_address = ORIGIN_MARKETPLACE_V1_CONTRACT_ADDRESS

        self.marketplace_listing_exporter = marketplace_listing_exporter
        self.shop_listing_exporter = shop_listing_exporter

        self.batch_work_executor = BatchWorkExecutor(batch_size, max_workers)

        self.event_extractor = OriginEventExtractor()

        self.receipt_log_mapper = EthReceiptLogMapper()
        self.marketplace_listing_mapper = OriginMarketplaceListingMapper()
        self.shop_listing_mapper = OriginShopListingMapper()


    def _start(self):
        self.marketplace_listing_exporter.open()
        self.shop_listing_exporter.open()

    def _export(self):
        self.batch_work_executor.execute(
            range(self.start_block, self.end_block + 1),
            self._export_batch,
            total_items=self.end_block - self.start_block + 1
        )

    def _export_batch(self, block_number_batch):
        assert len(block_number_batch) > 0
        # https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getfilterlogs
        filter_params = {
            'address': self.contract_address,
            'fromBlock': block_number_batch[0],
            'toBlock': block_number_batch[-1]
        }

        event_filter = self.web3.eth.filter(filter_params)
        events = event_filter.get_all_entries()
        for event in events:
            log = self.receipt_log_mapper.web3_dict_to_receipt_log(event)
            listing, shop_listings = self.event_extractor.extract_event_from_log(log)
            if listing:
                item = self.marketplace_listing_mapper.listing_to_dict(listing)
                self.marketplace_listing_exporter.export_item(item)
            for shop_listing in shop_listings:
                item = self.shop_listing_mapper.listing_to_dict(shop_listing)
                self.shop_listing_exporter.export_item(item)

        self.web3.eth.uninstallFilter(event_filter.filter_id)

    def _end(self):
        self.batch_work_executor.shutdown()
        self.marketplace_listing_exporter.close()
        self.shop_listing_exporter.close()