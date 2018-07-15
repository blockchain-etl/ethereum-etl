# MIT License
#
# Copyright (c) 2018 Evgeny Medvedev, evge.medvedev@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import argparse

from web3 import IPCProvider, Web3

from ethereumetl.file_utils import smart_open
from ethereumetl.jobs.export_erc20_tokens_job import ExportErc20TokensJob
from ethereumetl.jobs.export_erc20_tokens_job_item_exporter import export_erc20_tokens_job_item_exporter
from ethereumetl.thread_local_proxy import ThreadLocalProxy

parser = argparse.ArgumentParser(description='Exports ERC20 tokens.')
parser.add_argument('-t', '--token-addresses', type=str, help='The file containing token addresses, one per line.')
parser.add_argument('-o', '--output', default='-', type=str, help='The output file. If not specified stdout is used.')
parser.add_argument('-w', '--max-workers', default=5, type=int, help='The maximum number of workers.')
parser.add_argument('--ipc-path', required=True, type=str, help='The full path to the ipc socket file.')
parser.add_argument('--ipc-timeout', default=60, type=int, help='The timeout in seconds for ipc calls.')

args = parser.parse_args()

with smart_open(args.token_addresses, 'r') as token_addresses_file:
    job = ExportErc20TokensJob(
        token_addresses_iterable=(token_address.strip() for token_address in token_addresses_file),
        web3=ThreadLocalProxy(lambda: Web3(IPCProvider(args.ipc_path, timeout=args.ipc_timeout))),
        item_exporter=export_erc20_tokens_job_item_exporter(args.output),
        max_workers=args.max_workers)

    job.run()
