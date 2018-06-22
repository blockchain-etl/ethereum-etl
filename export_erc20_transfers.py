import argparse

from web3 import IPCProvider, Web3

from ethereumetl.exporters import CsvItemExporter
from ethereumetl.mapper.erc20_transfer_mapper import EthErc20TransferMapper
from ethereumetl.mapper.transaction_receipt_log_mapper import EthTransactionReceiptLogMapper
from ethereumetl.service.erc20_processor import EthErc20Processor, TRANSFER_EVENT_TOPIC
from ethereumetl.utils import smart_open

parser = argparse.ArgumentParser(
    description='Exports ERC20 transfers using eth_newFilter and eth_getFilterLogs JSON RPC APIs.')
parser.add_argument('--start-block', default=0, type=int, help='Start block')
parser.add_argument('--end-block', required=True, type=int, help='End block')
parser.add_argument('--output', default=None, type=str, help='The output file. If not specified stdout is used.')
parser.add_argument('--ipc-path', required=True, type=str, help='The full path to the ipc socket file.')
parser.add_argument('--ipc-timeout', default=300, type=int, help='The timeout in seconds for ipc calls.')
parser.add_argument('--batch-size', default=100, type=int, help='The number of blocks to filter at a time.')

args = parser.parse_args()


with smart_open(args.output, binary=True) as output_file:
    transaction_receipt_log_mapper = EthTransactionReceiptLogMapper()
    erc20_transfer_mapper = EthErc20TransferMapper()
    erc20_processor = EthErc20Processor()
    exporter = CsvItemExporter(output_file)

    web3 = Web3(IPCProvider(args.ipc_path, timeout=args.ipc_timeout))

    for batch_start_block in range(args.start_block, args.end_block + 1, args.batch_size):
        batch_end_block = min(batch_start_block + args.batch_size - 1, args.end_block)

        event_filter = web3.eth.filter({
            "fromBlock": batch_start_block,
            "toBlock": batch_end_block,
            "topics": [TRANSFER_EVENT_TOPIC]
        })

        events = event_filter.get_all_entries()

        for event in events:
            log = transaction_receipt_log_mapper.web3_dict_to_transaction_receipt_log(event)
            erc20_transfer = erc20_processor.filter_transfer_from_receipt_log(log)
            if erc20_transfer is not None:
                exporter.export_item(erc20_transfer_mapper.erc20_transfer_to_dict(erc20_transfer))

        web3.eth.uninstallFilter(event_filter.filter_id)
