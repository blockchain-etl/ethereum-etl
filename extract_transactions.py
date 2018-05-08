import argparse
import json

from ethereumetl.exporters import CsvItemExporter
from ethereumetl.mapper.block_mapper import EthBlockMapper
from ethereumetl.mapper.transaction_mapper import EthTransactionMapper
from ethereumetl.utils import smart_open

parser = argparse.ArgumentParser(description='Extract transactions from eth_getBlockByNumber JSON RPC output')
parser.add_argument('--input', default=None, type=str, help='The input file. If not specified stdin is used.')
parser.add_argument('--output', default=None, type=str, help='The output file. If not specified stdout is used.')

args = parser.parse_args()

with smart_open(args.input, 'r') as input_file, smart_open(args.output, binary=True) as output_file:
    block_mapper = EthBlockMapper()
    transaction_mapper = EthTransactionMapper()

    exporter = CsvItemExporter(output_file)
    exporter.start_exporting()
    for line in input_file:
        json_line = json.loads(line)
        result = json_line.get('result', None)
        if result is None:
            continue
        block = block_mapper.json_dict_to_block(result)
        if block.transactions is not None:
            for transaction in block.transactions:
                exporter.export_item(transaction_mapper.transaction_to_dict(transaction))
    exporter.finish_exporting()




