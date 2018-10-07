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
from datetime import datetime, timedelta

from web3 import Web3

from ethereumetl.providers.auto import get_provider_from_uri
from ethereumetl.service.eth_service import EthService
from export_all_common import export_all

parser = argparse.ArgumentParser(description='Export all for a range of blocks.',
                                 usage='-s <start_date> -e <end_date> [-p <provider_uri>] '
                                       '[-o <output_dir>] [-w <max_workers>] [-B <export_batch_size>]')
parser.add_argument('-s', '--start-date', default='2015-07-30', type=str, help='Start date (YYYY-MM-DD)')
parser.add_argument('-e', '--end-date', required=True, type=str, help='End date (YYYY-MM-DD)')
parser.add_argument('-p', '--provider-uri', default='https://mainnet.infura.io', type=str,
                    help='The URI of the web3 provider e.g. '
                         'file://$HOME/Library/Ethereum/geth.ipc or https://mainnet.infura.io')
parser.add_argument('-o', '--output-dir', default='output', type=str, help='Output directory, partitioned in Hive style.')
parser.add_argument('-w', '--max-workers', default=5, type=int, help='The maximum number of workers.')
parser.add_argument('-B', '--export-batch-size', default=100, type=int, help='The number of rows to write concurrently.')

args = parser.parse_args()


def get_partitions():
    provider = get_provider_from_uri(args.provider_uri)
    web3 = Web3(provider)
    eth_service = EthService(web3)

    start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date()
    day = timedelta(days=1)

    while start_date <= end_date:
        batch_start_block, batch_end_block = eth_service.get_block_range_for_date(start_date)

        partition_dir = '/date=' + str(start_date)

        yield batch_start_block, batch_end_block, partition_dir

        start_date += day


export_all(get_partitions(), args.output_dir, args.provider_uri, args.max_workers, args.export_batch_size)
