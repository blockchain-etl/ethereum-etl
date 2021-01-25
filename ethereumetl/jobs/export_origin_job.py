from ethereumetl.executors.batch_work_executor import BatchWorkExecutor
from blockchainetl.jobs.base_job import BaseJob
from ethereumetl.utils import validate_range

from ethereumetl.mappers.receipt_log_mapper import EthReceiptLogMapper
from ethereumetl.mappers.origin_mapper import OriginMarketplaceListingMapper, OriginShopProductMapper
from ethereumetl.service.origin_extractor import OriginEventExtractor


# Addresses of the marketplace contracts.
ORIGIN_MARKETPLACE_V0_CONTRACT_ADDRESS = '0x819Bb9964B6eBF52361F1ae42CF4831B921510f9'
ORIGIN_MARKETPLACE_V1_CONTRACT_ADDRESS = '0x698Ff47B84837d3971118a369c570172EE7e54c2'

# Block number at which contracts were deployed to the Mainnet.
ORIGIN_MARKETPLACE_V0_BLOCK_NUMBER_EPOCH = 6436157
ORIGIN_MARKETPLACE_V1_BLOCK_NUMBER_EPOCH = 8582597


class ExportOriginJob(BaseJob):
    def __init__(
            self,
            start_block,
            end_block,
            batch_size,
            web3,
            ipfs_client,
            marketplace_listing_exporter,
            shop_product_exporter,
            max_workers):
        validate_range(start_block, end_block)
        self.start_block = start_block
        self.end_block = end_block

        self.web3 = web3

        self.marketplace_listing_exporter = marketplace_listing_exporter
        self.shop_product_exporter = shop_product_exporter

        self.batch_work_executor = BatchWorkExecutor(batch_size, max_workers)

        self.event_extractor = OriginEventExtractor(ipfs_client)

        self.receipt_log_mapper = EthReceiptLogMapper()
        self.marketplace_listing_mapper = OriginMarketplaceListingMapper()
        self.shop_listing_mapper = OriginShopProductMapper()


    def _start(self):
        self.marketplace_listing_exporter.open()
        self.shop_product_exporter.open()

    def _export(self):
        self.batch_work_executor.execute(
            range(self.start_block, self.end_block + 1),
            self._export_batch,
            total_items=self.end_block - self.start_block + 1
        )

    def _export_batch(self, block_number_batch):
        assert len(block_number_batch) > 0

        from_block = block_number_batch[0]
        to_block = block_number_batch[-1]

        # Nothing to process if the block range is older than the V0 marketplace contract's epoch.
        if to_block < ORIGIN_MARKETPLACE_V0_BLOCK_NUMBER_EPOCH:
            return

        # Determine the version and address of the marketplace contract to query based on the block range.
        batches = []
        if to_block < ORIGIN_MARKETPLACE_V1_BLOCK_NUMBER_EPOCH or from_block >= ORIGIN_MARKETPLACE_V1_BLOCK_NUMBER_EPOCH:
            # The block range falls within a single version of the marketplace contract.
            version = '000' if to_block < ORIGIN_MARKETPLACE_V1_BLOCK_NUMBER_EPOCH else '001'
            address = ORIGIN_MARKETPLACE_V0_CONTRACT_ADDRESS if version == '000' else ORIGIN_MARKETPLACE_V1_CONTRACT_ADDRESS
            batches.append({
                'contract_address': address,
                'contract_version': version,
                'from_block': from_block,
                'to_block': to_block
            })
        else:
            # The block range spans across 2 versions of the marketplace contract.
            batches.append({
                'contract_address': ORIGIN_MARKETPLACE_V0_CONTRACT_ADDRESS,
                'contract_version': '000',
                'from_block': from_block,
                'to_block': ORIGIN_MARKETPLACE_V1_BLOCK_NUMBER_EPOCH - 1
            })
            batches.append({
                'contract_address': ORIGIN_MARKETPLACE_V1_CONTRACT_ADDRESS,
                'contract_version': '001',
                'from_block': ORIGIN_MARKETPLACE_V1_BLOCK_NUMBER_EPOCH,
                'to_block': to_block
            })

        for batch in batches:
            # https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getfilterlogs
            filter_params = {
                'address': batch['contract_address'],
                'fromBlock': batch['from_block'],
                'toBlock': batch['to_block']
            }
            event_filter = self.web3.eth.filter(filter_params)
            events = event_filter.get_all_entries()
            for event in events:
                log = self.receipt_log_mapper.web3_dict_to_receipt_log(event)
                listing, shop_products = self.event_extractor.extract_event_from_log(log, batch['contract_version'])
                if listing:
                    item = self.marketplace_listing_mapper.listing_to_dict(listing)
                    self.marketplace_listing_exporter.export_item(item)
                for product in shop_products:
                    item = self.shop_listing_mapper.product_to_dict(product)
                    self.shop_product_exporter.export_item(item)

            self.web3.eth.uninstallFilter(event_filter.filter_id)

    def _end(self):
        self.batch_work_executor.shutdown()
        self.marketplace_listing_exporter.close()
        self.shop_product_exporter.close()