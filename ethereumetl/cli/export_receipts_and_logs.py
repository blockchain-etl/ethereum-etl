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


import click

from blockchainetl.file_utils import smart_open
from ethereumetl.jobs.export_receipts_job import ExportReceiptsJob
from ethereumetl.jobs.exporters.receipts_and_logs_item_exporter import receipts_and_logs_item_exporter
from blockchainetl.logging_utils import logging_basic_config
from ethereumetl.thread_local_proxy import ThreadLocalProxy
from ethereumetl.providers.auto import get_provider_from_uri
from ethereumetl.utils import check_classic_provider_uri

logging_basic_config()


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-b', '--batch-size', default=100, show_default=True, type=int, help='The number of receipts to export at a time.')
@click.option('-t', '--transaction-hashes', required=True, type=str,
              help='The file containing transaction hashes, one per line.')
@click.option('-p', '--provider-uri', default='https://mainnet.infura.io', show_default=True, type=str,
              help='The URI of the web3 provider e.g. '
                   'file://$HOME/Library/Ethereum/geth.ipc or https://mainnet.infura.io')
@click.option('-w', '--max-workers', default=5, show_default=True, type=int, help='The maximum number of workers.')
@click.option('--receipts-output', default=None, show_default=True, type=str,
              help='The output file for receipts. If not provided receipts will not be exported. Use "-" for stdout')
@click.option('--logs-output', default=None, show_default=True, type=str,
              help='The output file for receipt logs. '
                   'aIf not provided receipt logs will not be exported. Use "-" for stdout')
@click.option('-c', '--chain', default='ethereum', show_default=True, type=str, help='The chain network to connect to.')
def export_receipts_and_logs(batch_size, transaction_hashes, provider_uri, max_workers, receipts_output, logs_output,
                             chain='ethereum'):
    """Exports receipts and logs."""
    provider_uri = check_classic_provider_uri(chain, provider_uri)
    with smart_open(transaction_hashes, 'r') as transaction_hashes_file:
        job = ExportReceiptsJob(
            transaction_hashes_iterable=(transaction_hash.strip() for transaction_hash in transaction_hashes_file),
            batch_size=batch_size,
            batch_web3_provider=ThreadLocalProxy(lambda: get_provider_from_uri(provider_uri, batch=True)),
            max_workers=max_workers,
            item_exporter=receipts_and_logs_item_exporter(receipts_output, logs_output),
            export_receipts=receipts_output is not None,
            export_logs=logs_output is not None)

        job.run()
