import json
import argparse

from builtins import str

from ethereumetl.utils import smart_open

parser = argparse.ArgumentParser(
    description='Generate Ethereum eth_getBlockByNumber JSON RPC call inputs for a block range')
parser.add_argument('--start-block', default=0, type=int, help='Start block')
parser.add_argument('--end-block', required=True, type=int, help='End block')
parser.add_argument('--output', default=None, type=str, help='The output file. If not specified stdout is used.')

args = parser.parse_args()


def generate_get_block_by_number_json_rpc(start_block, end_block):
    for block_number in range(start_block, end_block + 1):
        yield {
            'jsonrpc': '2.0',
            'method': 'eth_getBlockByNumber',
            'params': [hex(block_number), True],
            'id': 1,
        }


with smart_open(args.output) as output_file:
    for data in generate_get_block_by_number_json_rpc(args.start_block, args.end_block):
        output_file.write(json.dumps(data) + '\n')
