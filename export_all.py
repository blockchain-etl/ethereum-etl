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
import re

from datetime import datetime, timedelta
from export_all_common import export_all
from web3 import Web3

from ethereumetl.providers.auto import get_provider_from_uri
from ethereumetl.service.eth_service import EthService

parser = argparse.ArgumentParser(description='Export all for a range of blocks.',
                                 usage='-s <start> -e <end> [-b <partition_batch_size>] [-p <provider_uri>] '
                                       '[-o <output_dir>] [-w <max_workers>] [-B <export_batch_size>]')
parser.add_argument('-s', '--start', required=True, type=str, help='Start block/ISO date/Unix time')
parser.add_argument('-e', '--end', required=True, type=str, help='End block/ISO date/Unix time')
parser.add_argument('-b', '--partition-batch-size', default=10000, type=int,
                    help='The number of blocks to export in partition.')
parser.add_argument('-p', '--provider-uri', default='https://mainnet.infura.io', type=str,
                    help='The URI of the web3 provider e.g. '
                         'file://$HOME/Library/Ethereum/geth.ipc or https://mainnet.infura.io')
parser.add_argument('-o', '--output-dir', default='output', type=str,
                    help='Output directory, partitioned in Hive style.')
parser.add_argument('-w', '--max-workers', default=5, type=int, help='The maximum number of workers.')
parser.add_argument('-B', '--export-batch-size', default=100, type=int,
                    help='The number of rows to write concurrently.')

args = parser.parse_args()


def is_date_range(start, end):
    """Checks for YYYY-MM-DD date format."""
    return bool(re.match('^2[0-9]{3}-[0-9]{2}-[0-9]{2}$', start) and
                re.match('^2[0-9]{3}-[0-9]{2}-[0-9]{2}$', end))


def is_unix_time_range(start, end):
    """Checks for Unix timestamp format."""
    return bool(re.match("^[0-9]{10}$|^[0-9]{13}$", start) and
                re.match("^[0-9]{10}$|^[0-9]{13}$", end))


def is_block_range(start, end):
    """Checks for a valid block number."""
    return (start.isdigit() and 0 <= int(start) <= 99999999 and
            end.isdigit() and 0 <= int(end) <= 99999999)


def get_partitions():
    if is_date_range(args.start, args.end) or is_unix_time_range(args.start, args.end):
        if is_date_range(args.start, args.end):
            start_date = datetime.strptime(args.start, '%Y-%m-%d').date()
            end_date = datetime.strptime(args.end, '%Y-%m-%d').date()

        elif is_unix_time_range(args.start, args.end):
            if len(args.start) == 10 and len(args.end) == 10:
                start_date = datetime.utcfromtimestamp(int(args.start)).date()
                end_date = datetime.utcfromtimestamp(int(args.end)).date()

            elif len(args.start) == 13 and len(args.end) == 13:
                start_date = datetime.utcfromtimestamp(int(args.start) / 1e3).date()
                end_date = datetime.utcfromtimestamp(int(args.end) / 1e3).date()

        day = timedelta(days=1)

        provider = get_provider_from_uri(args.provider_uri)
        web3 = Web3(provider)
        eth_service = EthService(web3)

        while start_date <= end_date:
            batch_start_block, batch_end_block = eth_service.get_block_range_for_date(start_date)
            partition_dir = '/date=' + str(start_date)
            yield batch_start_block, batch_end_block, partition_dir
            start_date += day

    elif is_block_range(args.start, args.end):
        start_block = int(args.start)
        end_block = int(args.end)

        for batch_start_block in range(start_block, end_block + 1, args.partition_batch_size):
            batch_end_block = batch_start_block + args.partition_batch_size - 1
            if batch_end_block > end_block:
                batch_end_block = end_block

            padded_batch_start_block = str(batch_start_block).zfill(8)
            padded_batch_end_block = str(batch_end_block).zfill(8)
            partition_dir = f'/start_block={padded_batch_start_block}/end_block={padded_batch_end_block}'
            yield batch_start_block, batch_end_block, partition_dir

    else:
        raise ValueError('start and end must be either block numbers or ISO dates or Unix times')


export_all(get_partitions(), args.output_dir, args.provider_uri, args.max_workers, args.export_batch_size)
