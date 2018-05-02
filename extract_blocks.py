import argparse
import fileinput
import json

from ethereumetl.exporters import CsvItemExporter
from ethereumetl.mapper.block_mapper import EthBlockMapper
from ethereumetl.utils import smart_open

parser = argparse.ArgumentParser(description='Extract blocks from eth_getBlockByNumber JSON RPC output')
parser.add_argument('--input', default=None, type=str, help='The input file. If not specified stdin is used.')
parser.add_argument('--output', default=None, type=str, help='The output file. If not specified stdout is used.')

args = parser.parse_args()

with smart_open(args.output, binary=True) as output_handle:
    block_mapper = EthBlockMapper()

    exporter = CsvItemExporter(output_handle)
    exporter.start_exporting()
    for line in fileinput.input(files=args.input):
        json_line = json.loads(line)
        result = json_line.get('result', None)
        if result is None:
            continue
        block = block_mapper.json_dict_to_block(result)
        exporter.export_item(block_mapper.block_to_dict(block))
    exporter.finish_exporting()




