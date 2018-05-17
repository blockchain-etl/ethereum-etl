import json
import argparse

from builtins import str

from ethereumetl.argparse_utils import str_to_bool
from ethereumetl.utils import smart_open, batch

parser = argparse.ArgumentParser(
    description='Generate Ethereum eth_getBlockByNumber JSON RPC call inputs for a block range')
parser.add_argument('--start-block', default=0, type=int, help='Start block')
parser.add_argument('--end-block', required=True, type=int, help='End block')
parser.add_argument('--include-transactions', const=True, default=True, type=str_to_bool, nargs='?',
                    help='Whether or not to include transactions')
parser.add_argument('--output', default=None, type=str, help='The output file. If not specified stdout is used.')
parser.add_argument('--batch-size', default=100, type=int, help='The number of blocks in a batch.')

args = parser.parse_args()


def generate_get_block_by_number_json_rpc(start_block, end_block, include_transactions):
    for block_number in range(start_block, end_block + 1):
        yield {
            'jsonrpc': '2.0',
            'method': 'eth_getBlockByNumber',
            'params': [hex(block_number), include_transactions],
            'id': 1,
        }


with smart_open(args.output) as output_file:
    blocks_rpc = generate_get_block_by_number_json_rpc(args.start_block, args.end_block, args.include_transactions)

    for batch in batch(blocks_rpc, args.batch_size):
        output_file.write(json.dumps(batch) + '\n')
