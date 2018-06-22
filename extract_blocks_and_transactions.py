import argparse
import json

from ethereumetl.exporters import CsvItemExporter
from ethereumetl.mapper.block_mapper import EthBlockMapper
from ethereumetl.mapper.transaction_mapper import EthTransactionMapper
from ethereumetl.utils import smart_open

# parser用来设定命令行的一些参数
parser = argparse.ArgumentParser(
    description='Extract blocks and transactions from eth_getBlockByNumber JSON RPC output')
parser.add_argument('--input', default=None, type=str, help='The input file. If not specified stdin is used.')
parser.add_argument('--blocks-output', default=None, type=str,
                    help='The output file for blocks. If not specified stdout is used.')
parser.add_argument('--transactions-output', default=None, type=str,
                    help='The output file for transactions. If not specified stdout is used.')

args = parser.parse_args()

with smart_open(args.input, 'r') as input_file, \
        smart_open(args.blocks_output, binary=True) as blocks_output_file, \
        smart_open(args.transactions_output, binary=True) as tx_output_file:
    block_mapper = EthBlockMapper()
    # mapper是在把数据进行转化
    tx_mapper = EthTransactionMapper()

    blocks_exporter = CsvItemExporter(blocks_output_file)
    # 导出csv文件的类
    tx_exporter = CsvItemExporter(tx_output_file)

    for line in input_file:
        json_line = json.loads(line)
        result = json_line.get('result', None)
        if result is None:
            continue
        block = block_mapper.json_dict_to_block(result)
        blocks_exporter.export_item(block_mapper.block_to_dict(block))

        if block.transactions is not None:
            for transaction in block.transactions:
                tx_exporter.export_item(tx_mapper.transaction_to_dict(transaction))
