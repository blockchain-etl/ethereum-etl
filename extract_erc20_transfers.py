import argparse
import fileinput
import json

from ethereumetl.exporters import CsvItemExporter
from ethereumetl.mapper.erc20_transfer_mapper import EthErc20TransferMapper
from ethereumetl.mapper.transaction_receipt_mapper import EthTransactionReceiptMapper
from ethereumetl.service.erc20_processor import EthErc20Processor
from ethereumetl.utils import smart_open

parser = argparse.ArgumentParser(description='Extract ERC20 transfers from eth_getTransactionReceipt JSON RPC output')
parser.add_argument('--input', default=None, type=str, help='The input file. If not specified stdin is used.')
parser.add_argument('--output', default=None, type=str, help='The output file. If not specified stdout is used.')

args = parser.parse_args()

with smart_open(args.output, binary=True) as output_handle:
    transaction_receipt_mapper = EthTransactionReceiptMapper()
    erc20_transfer_mapper = EthErc20TransferMapper()
    erc20_processor = EthErc20Processor()

    exporter = CsvItemExporter(output_handle)
    exporter.start_exporting()
    for line in fileinput.input(files=args.input):
        json_line = json.loads(line)
        result = json_line.get('result', None)
        if result is None:
            continue
        receipt = transaction_receipt_mapper.json_dict_to_transaction_receipt(result)

        erc20_transfers = erc20_processor.filter_transfers_from_receipt(receipt)

        for erc20_transfer in erc20_transfers:
            exporter.export_item(erc20_transfer_mapper.erc20_transfer_to_dict(erc20_transfer))
    exporter.finish_exporting()




