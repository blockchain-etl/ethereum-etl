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
    ipc_providers = [IPCProvider(args.ipc_path) for _ in range(0, args.batch_size + 1)]
    for line in input_file:
        if len(ipc_providers) == 0:
            first_future = futures.pop(0)
            response = first_future.result()
            output_file.write(response + '\n')
            ipc_providers.append(first_future.ipc_provider)

        ipc_provider = ipc_providers.pop()

        def task():
            return ipc_provider.make_request(line)

        future = executor.submit(task)
        future.ipc_provider = ipc_provider
        futures.append(future)



    for fut in futures:
        output_file.write(fut.result() + '\n')

    executor.shutdown(wait=True)

    end = time.time()
    print('Running time is {} seconds'.format((end - start)))

