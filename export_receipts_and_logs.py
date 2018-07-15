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

from ethereumetl.file_utils import smart_open
from ethereumetl.jobs.export_receipts_job import ExportReceiptsJob
from ethereumetl.jobs.export_receipts_job_item_exporter import export_receipts_job_item_exporter
from ethereumetl.thread_local_proxy import ThreadLocalProxy
from ethereumetl.providers.auto import get_batch_provider_from_uri

parser = argparse.ArgumentParser(description='Export receipts and logs.')
parser.add_argument('-b', '--batch-size', default=100, type=int, help='The number of receipts to export at a time.')
parser.add_argument('-t', '--tx-hashes', type=str, help='The file containing transaction hashes, one per line.')
parser.add_argument('-p', '--provider-uri', required=True, type=str,
                    help='The URI of the web3 provider e.g. '
                         'file:///$HOME/Library/Ethereum/geth.ipc or https://mainnet.infura.io/')
parser.add_argument('-w', '--max-workers', default=5, type=int, help='The maximum number of workers.')
parser.add_argument('--receipts-output', default=None, type=str,
                    help='The output file for receipts. If not provided receipts will not be exported. '
                         'Use "-" for stdout')
parser.add_argument('--logs-output', default=None, type=str,
                    help='The output file for receipt logs. If not provided receipt logs will not be exported. '
                         'Use "-" for stdout')

args = parser.parse_args()

with smart_open(args.tx_hashes, 'r') as tx_hashes_file:
    job = ExportReceiptsJob(
        tx_hashes_iterable=(tx_hash.strip() for tx_hash in tx_hashes_file),
        batch_size=args.batch_size,
        batch_web3_provider=ThreadLocalProxy(lambda: get_batch_provider_from_uri(args.provider_uri)),
        max_workers=args.max_workers,
        item_exporter=export_receipts_job_item_exporter(args.receipts_output, args.logs_output),
        export_receipts=args.receipts_output is not None,
        export_logs=args.logs_output is not None)

    job.run()
