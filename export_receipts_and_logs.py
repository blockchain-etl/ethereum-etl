#!/usr/bin/env python3
import argparse

from ethereumetl.file_utils import smart_open
from ethereumetl.ipc import IPCWrapper
from ethereumetl.jobs.export_receipts_job import ExportReceiptsJob
from ethereumetl.jobs.export_receipts_job_item_exporter import export_receipts_job_item_exporter
from ethereumetl.thread_local_proxy import ThreadLocalProxy

parser = argparse.ArgumentParser(description='Export receipts and logs.')
parser.add_argument('-b', '--batch-size', default=100, type=int, help='The number of receipts to export at a time.')
parser.add_argument('-t', '--tx-hashes', type=str, help='The file containing transaction hashes, one per line.')
parser.add_argument('--ipc-path', required=True, type=str, help='The full path to the ipc file.')
parser.add_argument('--ipc-timeout', default=300, type=int, help='The timeout in seconds for ipc calls.')
parser.add_argument('-w', '--max-workers', default=5, type=int, help='The maximum number of workers.')
parser.add_argument('--receipts-output', default=None, type=str,
                    help='The output file for receipts. If not provided receipts will not be exported. '
                         'Use "-" for stdout')
parser.add_argument('--logs-output', default=None, type=str,
                    help='The output file for receipt logs. If not provided receipt logs will not be exported. '
                         'Use "-" for stdout')

args = parser.parse_args()

with smart_open(args.tx_hashes, 'r') as tx_hashes_file:
    job = ExportReceiptsJob(
        tx_hashes_iterable=(tx_hash.strip() for tx_hash in tx_hashes_file),
        batch_size=args.batch_size,
        ipc_wrapper=ThreadLocalProxy(lambda: IPCWrapper(args.ipc_path, timeout=args.ipc_timeout)),
        max_workers=args.max_workers,
        item_exporter=export_receipts_job_item_exporter(args.receipts_output, args.logs_output),
        export_receipts=args.receipts_output is not None,
        export_logs=args.logs_output is not None)

    job.run()
