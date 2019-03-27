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

import logging

import click
from ethereumetl.enumeration.entity_type import EntityType

from ethereumetl.logging_utils import logging_basic_config
from ethereumetl.providers.auto import get_provider_from_uri
from ethereumetl.thread_local_proxy import ThreadLocalProxy


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-l', '--last-synced-block-file', default='last_synced_block.txt', type=str, help='')
@click.option('--lag', default=0, type=int, help='The number of blocks to lag behind the network.')
@click.option('-p', '--provider-uri', default='https://mainnet.infura.io', type=str,
              help='The URI of the web3 provider e.g. '
                   'file://$HOME/Library/Ethereum/geth.ipc or https://mainnet.infura.io')
@click.option('-t', '--output', type=str,
              help='Google PubSub topic path e.g. projects/your-project/topics/ethereum_blockchain. '
                   'If not specified will print to console')
@click.option('-s', '--start-block', default=None, type=int, help='Start block')
@click.option('-e', '--entity-types', default=EntityType.ALL_FOR_INFURA,
              type=click.Choice(EntityType.ALL_FOR_STREAMING), multiple=True,
              help='The list of entity types to export.')
@click.option('--period-seconds', default=10, type=int, help='How many seconds to sleep between syncs')
@click.option('-b', '--batch-size', default=10, type=int, help='How many blocks to batch in single request')
@click.option('-B', '--block-batch-size', default=1, type=int, help='How many blocks to batch in single sync round')
@click.option('-w', '--max-workers', default=5, type=int, help='The number of workers')
@click.option('--log-file', default=None, type=str, help='Log file')
def stream(last_synced_block_file, lag, provider_uri, output, start_block, entity_types,
           period_seconds=10, batch_size=2, block_batch_size=10, max_workers=5, log_file=None):
    """Streams all data types to console or Google Pub/Sub."""
    configure_logging(log_file)

    from ethereumetl.streaming.streaming_utils import get_item_exporter
    from ethereumetl.streaming.streamer import Streamer

    streamer = Streamer(
        batch_web3_provider=ThreadLocalProxy(lambda: get_provider_from_uri(provider_uri, batch=True)),
        last_synced_block_file=last_synced_block_file,
        lag=lag,
        item_exporter=get_item_exporter(output),
        start_block=start_block,
        period_seconds=period_seconds,
        batch_size=batch_size,
        block_batch_size=block_batch_size,
        max_workers=max_workers,
        entity_types=entity_types
    )
    streamer.stream()


def configure_logging(filename):
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging_basic_config(filename=filename)