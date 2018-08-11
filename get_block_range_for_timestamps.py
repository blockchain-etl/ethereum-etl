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

from web3 import Web3

from ethereumetl.file_utils import smart_open
from ethereumetl.logging_utils import logging_basic_config
from ethereumetl.providers.auto import get_provider_from_uri
from ethereumetl.service.eth_service import EthService

logging_basic_config()

parser = argparse.ArgumentParser(description='Outputs the start block and end block for a given timestamp range.')
parser.add_argument('-p', '--provider-uri', default='https://mainnet.infura.io', type=str,
                    help='The URI of the web3 provider e.g. '
                         'file://$HOME/Library/Ethereum/geth.ipc or https://mainnet.infura.io')
parser.add_argument('-s', '--start-timestamp', required=True, type=int, help='Start unix timestamp, in seconds.')
parser.add_argument('-e', '--end-timestamp', required=True, type=int, help='End unix timestamp, in seconds.')
parser.add_argument('-o', '--output', default='-', type=str, help='The output file. If not specified stdout is used.')

args = parser.parse_args()

provider = get_provider_from_uri(args.provider_uri)
web3 = Web3(provider)
eth_service = EthService(web3)

start_block, end_block = eth_service.get_block_range_for_timestamps(args.start_timestamp, args.end_timestamp)

with smart_open(args.output, 'w') as output_file:
    output_file.write('{},{}\n'.format(start_block, end_block))
