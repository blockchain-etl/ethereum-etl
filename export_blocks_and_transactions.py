#!/usr/bin/env python3
import argparse

from ethereumetl.ipc import IPCWrapper
from ethereumetl.job.export_blocks_job import ExportBlocksJob

parser = argparse.ArgumentParser(description='Export blocks and transactions.')
parser.add_argument('-s', '--start-block', default=0, type=int, help='Start block')
parser.add_argument('-e', '--end-block', required=True, type=int, help='End block')
parser.add_argument('-b', '--batch-size', default=100, type=int, help='The number of blocks to export at a time.')
parser.add_argument('-i', '--ipc-path', required=True, type=str, help='The full path to the ipc file.')
parser.add_argument('--ipc-timeout', default=300, type=int, help='The timeout in seconds for ipc calls.')
parser.add_argument('--max-workers', default=5, type=int, help='The maximum number of workers.')
parser.add_argument('--max-queue', default=5, type=int, help='The maximum number of tasks waiting in the queue.')
parser.add_argument('--blocks-output', default=None, type=str,
                    help='The output file for blocks. If not provided blocks will not be exported. '
                         'Use "-" for stdout')
parser.add_argument('--transactions-output', default=None, type=str,
                    help='The output file for transactions. If not provided transactions will not be exported. '
                         'Use "-" for stdout')

args = parser.parse_args()

job = ExportBlocksJob(
    start_block=args.start_block,
    end_block=args.end_block,
    batch_size=args.batch_size,
    ipc_wrapper_factory=lambda: IPCWrapper(args.ipc_path, args.ipc_timeout),
    max_workers=args.max_workers,
    max_queue=args.max_queue,
    blocks_output=args.blocks_output,
    transactions_output=args.transactions_output)

job.run()
