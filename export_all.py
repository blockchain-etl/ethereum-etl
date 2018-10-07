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

from export_all_common import export_all

parser = argparse.ArgumentParser(description='Export all for a range of blocks.',
                                 usage='-s <start_block> -e <end_block> [-b <partition_batch_size>] [-p <provider_uri>] '
                                       '[-o <output_dir>] [-w <max_workers>] [-B <export_batch_size>]')
parser.add_argument('-s', '--start-block', default=0, type=int, help='Start block')
parser.add_argument('-e', '--end-block', required=True, type=int, help='End block')
parser.add_argument('-b', '--partition-batch-size', default=10000, type=int,
                    help='The number of blocks to export in partition.')
parser.add_argument('-p', '--provider-uri', default='https://mainnet.infura.io', type=str,
                    help='The URI of the web3 provider e.g. '
                         'file://$HOME/Library/Ethereum/geth.ipc or https://mainnet.infura.io')
parser.add_argument('-o', '--output-dir', default='output', type=str,
                    help='Output directory, partitioned in Hive style.')
parser.add_argument('-w', '--max-workers', default=5, type=int, help='The maximum number of workers.')
parser.add_argument('-B', '--export-batch-size', default=100, type=int, help='The number of rows to write concurrently.')

args = parser.parse_args()


def get_partitions():
    for batch_start_block in range(args.start_block, args.end_block + 1, args.partition_batch_size):
        batch_end_block = batch_start_block + args.partition_batch_size - 1
        if batch_end_block > args.end_block:
            batch_end_block = args.end_block

        padded_batch_start_block = str(batch_start_block).zfill(8)
        padded_batch_end_block = str(batch_end_block).zfill(8)

        partition_dir = f'/start_block={padded_batch_start_block}/end_block={padded_batch_end_block}'

        yield batch_start_block, batch_end_block, partition_dir


export_all(get_partitions(), args.output_dir, args.provider_uri, args.max_workers, args.export_batch_size)
