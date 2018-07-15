import argparse
from datetime import datetime

from web3 import Web3

from ethereumetl.file_utils import smart_open
from ethereumetl.service.eth_service import EthService
from ethereumetl.web3_utils import get_provider_from_uri

parser = argparse.ArgumentParser(description='Outputs the start block and end block for a given date.')
parser.add_argument('-p', '--provider-uri', default=None, type=str,
                    help='The URI of the web3 provider e.g. file://$HOME/Library/Ethereum/geth.ipc. or https://mainnet.infura.io/')
parser.add_argument('-o', '--output', default='-', type=str, help='The output file. If not specified stdout is used.')
parser.add_argument('-d', '--date', required=True, type=lambda d: datetime.strptime(d, '%Y-%m-%d'),
                    help='The date e.g. 2018-01-01.')

args = parser.parse_args()

provider = get_provider_from_uri(args.provider_uri)
web3 = Web3(provider)
eth_service = EthService(web3)

start_block, end_block = eth_service.get_block_range_for_date(args.date)

with smart_open(args.output, 'w') as output_file:
    output_file.write('{},{}'.format(start_block, end_block))
