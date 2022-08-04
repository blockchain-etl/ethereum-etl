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

from blockchainetl.streaming.streaming_utils import configure_signals, configure_logging
from ethereumetl.enumeration.entity_type import EntityType
from ethereumetl.streaming.streaming import streaming


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-j', '--job-path-prefix', default='./', show_default=True, type=str, help='')
@click.option('--lag', default=0, show_default=True, type=int, help='The number of blocks to lag behind the network.')
@click.option('-p', '--provider-uri', default='https://mainnet.infura.io', show_default=True, type=str,
              help='The URI of the web3 provider e.g. '
                   'file://$HOME/Library/Ethereum/geth.ipc or https://mainnet.infura.io')
@click.option('-o', '--output', type=str,
              help='Either Google PubSub topic path e.g. projects/your-project/topics/crypto_ethereum; '
                   'or Postgres connection url e.g. postgresql+pg8000://postgres:admin@127.0.0.1:5432/ethereum; '
                   'or GCS bucket e.g. gs://your-bucket-name; '
                   'or kafka, output name and connection host:port e.g. kafka/127.0.0.1:9092 '
                   'If not specified will print to console')
@click.option('-s', '--start-block', default=None, show_default=True, type=int, help='Start block')
@click.option('-s', '--end-block', default=None, show_default=True, type=int, help='End block')
@click.option('-e', '--entity-types', default=','.join(EntityType.ALL_FOR_INFURA), show_default=True, type=str,
              help='The list of entity types to export.')
@click.option('--period-seconds', default=10, show_default=True, type=int,
              help='How many seconds to sleep between syncs')
@click.option('-b', '--batch-size', default=10, show_default=True, type=int,
              help='How many blocks to batch in single request')
@click.option('-B', '--block-batch-size', default=1, show_default=True, type=int,
              help='How many blocks to batch in single sync round')
@click.option('-w', '--max-workers', default=5, show_default=True, type=int, help='The number of workers')
@click.option('--log-file', default=None, show_default=True, type=str, help='Log file')
@click.option('--pid-file', default=None, show_default=True, type=str, help='pid file')
def stream(job_path_prefix, lag, provider_uri, output, start_block, end_block, entity_types,
           period_seconds, batch_size, block_batch_size, max_workers, log_file, pid_file):
    """Streams all data types to console or Google Pub/Sub."""
    configure_logging(log_file)
    configure_signals()

    streaming(
        output=output,
        entity_types=entity_types,
        provider_uri=provider_uri,
        max_workers=max_workers,
        batch_size=batch_size,
        block_batch_size=block_batch_size,
        start_block=start_block,
        end_block=end_block,
        node_index=0,
        job_path_prefix=job_path_prefix,
        lag=lag,
        period_seconds=period_seconds,
        log_file=log_file,
        pid_file=pid_file,
    )
