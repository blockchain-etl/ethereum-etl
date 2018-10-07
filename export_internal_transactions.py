# MIT License
#
# Copyright (c) 2018 Evgeniy Filatov, evgeniyfilatov@gmail.com
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

from web3 import Web3

from ethereumetl.jobs.export_internal_transactions_job import ExportInternalTransactionsJob
from ethereumetl.logging_utils import logging_basic_config
from ethereumetl.providers.auto import get_provider_from_uri
from ethereumetl.thread_local_proxy import ThreadLocalProxy
from ethereumetl.jobs.exporters.internal_transactions_item_exporter import internal_transactions_item_exporter

logging_basic_config()

parser = argparse.ArgumentParser(
    description='Exports internal transactions using trace_filter JSON RPC API.')
parser.add_argument('-s', '--start-block', default=0, type=int, help='Start block')
parser.add_argument('-e', '--end-block', required=True, type=int, help='End block')
parser.add_argument('-b', '--batch-size', default=100, type=int, help='The number of blocks to filter at a time.')
parser.add_argument('-o', '--output', default='-', type=str, help='The output file. If not specified stdout is used.')
parser.add_argument('-w', '--max-workers', default=5, type=int, help='The maximum number of workers.')
parser.add_argument('-p', '--provider-uri', required=True, type=str,
                    help='The URI of the web3 provider e.g. '
                         'file://$HOME/Library/Ethereum/geth.ipc or http://localhost:8545/')

args = parser.parse_args()

job = ExportInternalTransactionsJob(
    start_block=args.start_block,
    end_block=args.end_block,
    batch_size=args.batch_size,
    web3=ThreadLocalProxy(lambda: Web3(get_provider_from_uri(args.provider_uri))),
    item_exporter=internal_transactions_item_exporter(args.output),
    max_workers=args.max_workers)

job.run()
