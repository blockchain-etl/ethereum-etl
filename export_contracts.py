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

from ethereumetl.file_utils import smart_open
from ethereumetl.jobs.export_contracts_job import ExportContractsJob
from ethereumetl.jobs.export_contracts_job_item_exporter import export_contracts_job_item_exporter
from ethereumetl.thread_local_proxy import ThreadLocalProxy
from ethereumetl.web3_utils import get_batch_provider_from_uri

parser = argparse.ArgumentParser(
    description='Exports contracts bytecode using eth_getCode JSON RPC APIs.')
parser.add_argument('-b', '--batch-size', default=100, type=int, help='The number of blocks to filter at a time.')
parser.add_argument('-c', '--contract-addresses', type=str,
                    help='The file containing contract addresses, one per line.')
parser.add_argument('-o', '--output', default='-', type=str, help='The output file. If not specified stdout is used.')
parser.add_argument('-w', '--max-workers', default=5, type=int, help='The maximum number of workers.')
parser.add_argument('-p', '--provider-uri', required=True, type=str,
                    help='The URI of the web3 provider e.g. '
                         'file:///$HOME/Library/Ethereum/geth.ipc or https://mainnet.infura.io/')

args = parser.parse_args()

with smart_open(args.contract_addresses, 'r') as contract_addresses_file:
    contract_addresses = (contract_address.strip() for contract_address in contract_addresses_file
                          if contract_address.strip())
    job = ExportContractsJob(
        contract_addresses_iterable=contract_addresses,
        batch_size=args.batch_size,
        batch_web3_provider=ThreadLocalProxy(lambda: get_batch_provider_from_uri(args.provider_uri)),
        item_exporter=export_contracts_job_item_exporter(args.output),
        max_workers=args.max_workers)

    job.run()
