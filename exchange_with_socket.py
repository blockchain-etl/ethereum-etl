import argparse
import json
import threading

from web3 import IPCProvider

from ethereumetl.utils import smart_open

parser = argparse.ArgumentParser(
    description='Sends the given input to the socket and outputs its response')
parser.add_argument('--input', default=None, type=str, help='The input file. If not specified stdin is used.')
parser.add_argument('--output', default=None, type=str, help='The output file. If not specified stdout is used.')
parser.add_argument('--socket', required=True, type=str, help='The full path to the socket.')
parser.add_argument('--batch-size', default=1, type=int, help='The number of lines in the batch to send to socket.')


args = parser.parse_args()

with smart_open(args.input, 'r') as input_file, smart_open(args.output) as output_file:
    output_file_lock = threading.Lock()

    for line in input_file.readlines():
        request = json.loads(line)
        ipc_provider = IPCProvider(args.socket)
        response = ipc_provider.make_request(request['method'], request['params'])

        with output_file_lock:
            output_file.write(json.dumps(response) + '\n')

