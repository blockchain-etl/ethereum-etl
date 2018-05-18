import argparse
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from ethereumetl.ipc import IPCProvider
from ethereumetl.socket_utils import socket_exchange
from ethereumetl.utils import smart_open, batch_readlines

parser = argparse.ArgumentParser(
    description='Sends the given input to the ipc socket and outputs its response')
parser.add_argument('--input', default=None, type=str, help='The input file. If not specified stdin is used.')
parser.add_argument('--output', default=None, type=str, help='The output file. If not specified stdout is used.')
parser.add_argument('--ipc-path', required=True, type=str, help='The full path to the ipc socket file.')
parser.add_argument('--ipc-timeout', default=10, type=int, help='The timeout for ipc calls.')
parser.add_argument('--batch-size', default=100, type=int, help='The number of lines in the batch to send to socket.')


args = parser.parse_args()

with smart_open(args.input, 'r') as input_file, smart_open(args.output) as output_file:
    start = time.time()

    executor = ThreadPoolExecutor(max_workers=args.batch_size)
    futures = []
    ipc_providers = [IPCProvider(args.ipc_path)] * args.batch_size
    line_buffer = []
    for line in input_file:
        while True:
            if len(ipc_providers) == 0:
                time.sleep(0.1)
            else:
                ipc_provider = ipc_providers.pop()
                break

        def task():
            return ipc_provider.make_request(line)

        future = executor.submit(task)

        def got_result(fut):
            ipc_providers.append(ipc_provider)
            output_file.write(fut.result() + '\n')


        future.add_done_callback(got_result)


    for fut in futures:
        output_file.write(fut.result() + '\n')

    executor.shutdown(wait=True)

    end = time.time()
    print('Running time is {} seconds'.format((end - start)))

