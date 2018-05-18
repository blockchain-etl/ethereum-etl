import json

from ethereumetl.exporters import CsvItemExporter
from ethereumetl.file_utils import smart_open
from ethereumetl.ipc import BatchIPCProvider
from ethereumetl.json_rpc_requests import generate_get_block_by_number_json_rpc
from ethereumetl.mapper.block_mapper import EthBlockMapper
from ethereumetl.mapper.transaction_mapper import EthTransactionMapper
from ethereumetl.utils import batch_iterator


class EthEtlService(object):
    def export_blocks(self,
                      start_block,
                      end_block,
                      batch_size,
                      ipc_path=None,
                      ipc_timeout=10,
                      blocks_output=None,
                      transactions_output=None):
        export_blocks = blocks_output is not None
        export_transactions = transactions_output is not None
        if not export_blocks and not export_transactions:
            raise ValueError('Either blocks_output or transactions_output must be provided')

        block_mapper = EthBlockMapper()
        transaction_mapper = EthTransactionMapper()
        ipc_provider = self.create_ipc_provider(ipc_path, ipc_timeout)

        with smart_open(blocks_output, binary=True) as blocks_output_file, \
                smart_open(transactions_output, binary=True) as transactions_output_file:
            blocks_exporter = CsvItemExporter(blocks_output_file)
            transactions_exporter = CsvItemExporter(transactions_output_file)

            blocks_rpc = generate_get_block_by_number_json_rpc(start_block, end_block, export_blocks)

            for batch in batch_iterator(blocks_rpc, batch_size):
                response = ipc_provider.make_request(json.dumps(batch))
                for response_item in response:
                    result = response_item['result']
                    block = block_mapper.json_dict_to_block(result)
                    if export_blocks:
                        blocks_exporter.export_item(block_mapper.block_to_dict(block))
                    if export_transactions:
                        for tx in block.transactions:
                            transactions_exporter.export_item(transaction_mapper.transaction_to_dict(tx))

    def create_ipc_provider(self, ipc_path, timeout):
        return BatchIPCProvider(ipc_path, timeout=timeout)
