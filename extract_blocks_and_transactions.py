import argparse
import json

from ethereumetl.argparse_utils import str_to_bool
from ethereumetl.exporters import CsvItemExporter
from ethereumetl.mapper.block_mapper import EthBlockMapper
from ethereumetl.mapper.transaction_mapper import EthTransactionMapper
from ethereumetl.utils import smart_open

parser = argparse.ArgumentParser(
    description='Extract blocks and transactions from eth_getBlockByNumber JSON RPC output')
parser.add_argument('--input', default=None, type=str, help='The input file. If not specified stdin is used.')
parser.add_argument('--extract-blocks', const=True, default=True, type=str_to_bool, nargs='?',
                    help='Whether or not to extract blocks.')
parser.add_argument('--blocks-output', default=None, type=str,
                    help='The output file for blocks. If not specified stdout is used.')
parser.add_argument('--extract-transactions', const=True, default=True, type=str_to_bool, nargs='?',
                    help='Whether or not to extract transactions.')
parser.add_argument('--transactions-output', default=None, type=str,
                    help='The output file for transactions. If not specified stdout is used.')

args = parser.parse_args()

with smart_open(args.input, 'r') as input_file, \
        smart_open(args.blocks_output, binary=True) if args.extract_blocks else None as blocks_output_file, \
        smart_open(args.transactions_output, binary=True) if args.extract_transactions else None as tx_output_file:
    block_mapper = EthBlockMapper()
    tx_mapper = EthTransactionMapper()

    blocks_exporter = CsvItemExporter(blocks_output_file) if blocks_output_file is not None else None
    tx_exporter = CsvItemExporter(tx_output_file) if tx_output_file is not None else None

    for line in input_file:
        json_line = json.loads(line)
        result = json_line.get('result', None)
        if result is None:
            continue
        block = block_mapper.json_dict_to_block(result)
        if blocks_exporter is not None:
            blocks_exporter.export_item(block_mapper.block_to_dict(block))

        if block.transactions is not None and tx_exporter is not None:
            for transaction in block.transactions:
                tx_exporter.export_item(tx_mapper.transaction_to_dict(transaction))
