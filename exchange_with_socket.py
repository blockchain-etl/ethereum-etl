import argparse
import threading

from ethereumetl.socket_utils import exchange
from ethereumetl.utils import smart_open, batch_readlines

parser = argparse.ArgumentParser(
    description='Sends the given input to the socket and outputs its response')
parser.add_argument('--input', default=None, type=str, help='The input file. If not specified stdin is used.')
parser.add_argument('--output', default=None, type=str, help='The output file. If not specified stdout is used.')
parser.add_argument('--ipc-path', required=True, type=str, help='The full path to the ipc socket file.')
parser.add_argument('--batch-size', default=1, type=int, help='The number of lines in the batch to send to socket.')


args = parser.parse_args()

with smart_open(args.input, 'r') as input_file, smart_open(args.output) as output_file:
    output_file_lock = threading.Lock()

    for line_batch in batch_readlines(input_file, args.batch_size):
        response = exchange(args.ipc_path, ''.join(line_batch))

        with output_file_lock:
            output_file.write(response)

