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

from ethereumetl.jobs.export_pending_transactions_job import ExportPendingTransactionsJob
from ethereumetl.jobs.exporters.pending_transactions_item_exporter import pending_transactions_item_exporter
from ethereumetl.logging_utils import logging_basic_config
from ethereumetl.providers.auto import get_provider_from_uri
from ethereumetl.thread_local_proxy import ThreadLocalProxy

logging_basic_config()

parser = argparse.ArgumentParser(description='Export blocks and transactions.')
parser.add_argument('-p', '--provider-uri', required=True, type=str,
                    help='The URI of the web3 provider e.g. '
                         'file://$HOME/Library/Ethereum/geth.ipc or https://mainnet.infura.io')
parser.add_argument('-o', '--output', default=None, type=str,
                    help='The output file for pending transactions. '
                         'If not provided, pending transactions will not be exported. '
                         'Use "-" for stdout')
args = parser.parse_args()

job = ExportPendingTransactionsJob(
    batch_web3_provider=ThreadLocalProxy(lambda: get_provider_from_uri(args.provider_uri, batch=True)),
    item_exporter=pending_transactions_item_exporter(args.output),
    export_pending_transactions=args.output is not None)

job.run()
