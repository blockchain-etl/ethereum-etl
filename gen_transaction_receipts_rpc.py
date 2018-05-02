import json
import argparse

from builtins import str

from ethereumetl.utils import smart_open

parser = argparse.ArgumentParser(
    description='Generate Ethereum eth_getTransactionReceipt JSON RPC call inputs for given transaction hashes.')
parser.add_argument('--input', default=None, type=str, help='The input file. If not specified stdin is used.')
parser.add_argument('--output', default=None, type=str, help='The output file. If not specified stdout is used.')

args = parser.parse_args()


def generate_get_transaction_receipt_json_rpc(tx_hash):
    return {
        'jsonrpc': '2.0',
        'method': 'eth_getTransactionReceipt',
        'params': [tx_hash],
        'id': 1,
    }


with smart_open(args.input, 'r') as input_file:
    with smart_open(args.output, 'w') as output_file:
        for tx_hash in input_file.readlines():
            json_rpc = generate_get_transaction_receipt_json_rpc(tx_hash.rstrip())
            output_file.write(json.dumps(json_rpc))

