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


import click

from web3 import Web3

from ethereumetl.jobs.export_traces_job import ExportTracesJob
from blockchainetl.logging_utils import logging_basic_config
from ethereumetl.providers.auto import get_provider_from_uri
from ethereumetl.thread_local_proxy import ThreadLocalProxy
from ethereumetl.jobs.exporters.traces_item_exporter import traces_item_exporter

logging_basic_config()


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-s', '--start-block', default=0, show_default=True, type=int, help='Start block')
@click.option('-e', '--end-block', required=True, type=int, help='End block')
@click.option('-b', '--batch-size', default=5, show_default=True, type=int, help='The number of blocks to filter at a time.')
@click.option('-o', '--output', default='-', show_default=True, type=str, help='The output file. If not specified stdout is used.')
@click.option('-w', '--max-workers', default=5, show_default=True, type=int, help='The maximum number of workers.')
@click.option('-p', '--provider-uri', required=True, type=str,
              help='The URI of the web3 provider e.g. '
                   'file://$HOME/.local/share/io.parity.ethereum/jsonrpc.ipc or http://localhost:8545/')
@click.option('--genesis-traces/--no-genesis-traces', default=False, show_default=True, help='Whether to include genesis traces')
@click.option('--daofork-traces/--no-daofork-traces', default=False, show_default=True, help='Whether to include daofork traces')
@click.option('-t', '--timeout', default=60, show_default=True, type=int, help='IPC or HTTP request timeout.')
@click.option('-c', '--chain', default='ethereum', show_default=True, type=str, help='The chain network to connect to.')
def export_traces(start_block, end_block, batch_size, output, max_workers, provider_uri,
                  genesis_traces, daofork_traces, timeout=60, chain='ethereum'):
    """Exports traces from parity node."""
    if chain == 'classic' and daofork_traces == True:
        raise ValueError(
            'Classic chain does not include daofork traces. Disable daofork traces with --no-daofork-traces option.')
    job = ExportTracesJob(
        start_block=start_block,
        end_block=end_block,
        batch_size=batch_size,
        web3=ThreadLocalProxy(lambda: Web3(get_provider_from_uri(provider_uri, timeout=timeout))),
        item_exporter=traces_item_exporter(output),
        max_workers=max_workers,
        include_genesis_traces=genesis_traces,
        include_daofork_traces=daofork_traces)

    job.run()
