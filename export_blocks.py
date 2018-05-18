import argparse

from ethereumetl.ipc import IPCWrapper
from ethereumetl.jobs import ExportBlocksJob

parser = argparse.ArgumentParser(
    description='Exports blocks and transactions.')
parser.add_argument('--start-block', default=0, type=int, help='Start block')
parser.add_argument('--end-block', required=True, type=int, help='End block')
parser.add_argument('--batch-size', default=100, type=int, help='The number of blocks to filter at a time.')
parser.add_argument('--ipc-path', required=True, type=str, help='The full path to the ipc socket file.')
parser.add_argument('--ipc-timeout', default=300, type=int, help='The timeout in seconds for ipc calls.')
parser.add_argument('--blocks-output', default=None, type=str,
                    help='The output file for blocks. If not provided blocks will not be exported.')
parser.add_argument('--transactions-output', default=None, type=str,
                    help='The output file for transactions. If not provided transactions will not be exported.')

args = parser.parse_args()

job = ExportBlocksJob(start_block=args.start_block,
                      end_block=args.end_block,
                      batch_size=args.batch_size,
                      ipc_wrapper=IPCWrapper(args.ipc_path, args.ipc_timeout),
                      blocks_output=args.blocks_output,
                      transactions_output=args.transactions_output)

job.run()
