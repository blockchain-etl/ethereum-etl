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

from ethereumetl.jobs.export_geth_traces_job import ExportGethTracesJob
from ethereumetl.jobs.exporters.geth_traces_item_exporter import geth_traces_item_exporter
from ethereumetl.logging_utils import logging_basic_config
from ethereumetl.providers.auto import get_provider_from_uri
from ethereumetl.thread_local_proxy import ThreadLocalProxy

logging_basic_config()

parser = argparse.ArgumentParser(description='Export geth traces for further processing.')
parser.add_argument('-s', '--start-block', default=0, type=int, help='Start block')
parser.add_argument('-e', '--end-block', required=True, type=int, help='End block')
parser.add_argument('-b', '--batch-size', default=100, type=int, help='The number of blocks to export at a time.')
parser.add_argument('-p', '--provider-uri', default='https://mainnet.infura.io', type=str,
                    help='The URI of the web3 provider e.g. '
                         'file://$HOME/Library/Ethereum/geth.ipc')
parser.add_argument('-w', '--max-workers', default=5, type=int, help='The maximum number of workers.')
parser.add_argument('--geth-traces-output', default=None, type=str,
                    help='The output file for geth traces. Use "-" for stdout')

args = parser.parse_args()

job = ExportGethTracesJob(
    start_block=args.start_block,
    end_block=args.end_block,
    batch_size=args.batch_size,
    batch_web3_provider=ThreadLocalProxy(lambda: get_provider_from_uri(args.provider_uri, batch=True)),
    max_workers=args.max_workers,
    item_exporter=geth_traces_item_exporter(args.geth_traces_output))

job.run()
