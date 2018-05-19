#!/usr/bin/env python3
import argparse

from web3 import IPCProvider, Web3

from ethereumetl.jobs import ExportErc20TransfersJob

parser = argparse.ArgumentParser(
    description='Exports ERC20 transfers using eth_newFilter and eth_getFilterLogs JSON RPC APIs.')
parser.add_argument('--start-block', default=0, type=int, help='Start block')
parser.add_argument('--end-block', required=True, type=int, help='End block')
parser.add_argument('--batch-size', default=100, type=int, help='The number of blocks to filter at a time.')
parser.add_argument('--output', default='-', type=str, help='The output file. If not specified stdout is used.')
parser.add_argument('--tokens', default=None, type=str, help='Comma-separated list of token addresses to filter.')
parser.add_argument('--ipc-path', required=True, type=str, help='The full path to the ipc socket file.')
parser.add_argument('--ipc-timeout', default=300, type=int, help='The timeout in seconds for ipc calls.')

args = parser.parse_args()

job = ExportErc20TransfersJob(
    start_block=args.start_block,
    end_block=args.end_block,
    batch_size=args.batch_size,
    web3=Web3(IPCProvider(args.ipc_path, timeout=args.ipc_timeout)),
    output=args.output,
    tokens=args.tokens.strip().split(',') if args.tokens is not None else None)

job.run()
