import argparse

from ethereumetl.socket_utils import exchange_with_retries
from ethereumetl.utils import smart_open, batch_readlines

parser = argparse.ArgumentParser(
    description='Sends the given input to the socket and outputs its response')
parser.add_argument('--input', default=None, type=str, help='The input file. If not specified stdin is used.')
parser.add_argument('--output', default=None, type=str, help='The output file. If not specified stdout is used.')
parser.add_argument('--socket', required=True, type=str, help='The full path to the socket.')
# Use 1 for parity as it ignores some requests and behaves unreliable.
# Depending on RAM size use up to 100000 for geth.
parser.add_argument('--batch-size', default=1, type=int, help='The number of lines in the batch to send to socket.')
parser.add_argument('--max-retries', default=10, type=int,
                    help='The number of retries in case an exception is encountered.')
parser.add_argument('--timeout-seconds', default=10, type=int,
                    help='The number of seconds to wait for response from socket before throwing timeout.')

args = parser.parse_args()

is_parity = "parity" in args.socket.lower()

with smart_open(args.input, 'r') as input_file, smart_open(args.output) as output_file:
    for lines_batch in batch_readlines(input_file, args.batch_size):
        lines = ''.join(lines_batch)
        if is_parity:
            # Parity IPC somehow ignores the last line
            lines += '{}\n'
        response = exchange_with_retries(args.socket, lines, args.max_retries, args.timeout_seconds)
        output_file.write(response)
