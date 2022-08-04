import argparse

from ethereumetl.streaming.streaming import streaming
from hypernative.consts import NODE_PROVIDER
from hypernative.multi_node import get_block_indexes
from hypernative.output import generate_postgres_output
from hypernative.utils import get_job_path_prefix

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='transaction backfill parsing')
    parser.add_argument('-name', '--job_name', type=str, default='default',
                        help='the name of the current job (used for recovery)')
    parser.add_argument('-s', '--start_block_index', type=int, help='start block index')
    parser.add_argument('-e', '--end_block_index', type=int, help='end block index')
    parser.add_argument('-n', '--nodes', type=int, default=0, help='number of nodes')
    parser.add_argument('-i', '--node_index', type=int, default=0, help='index of current node')
    parser.add_argument('-w', '--max_workers', type=int, default=5, help='number of workers per process')
    parser.add_argument('-provider', '--provider_uri', type=str, default=NODE_PROVIDER, help='provider uri')
    parser.add_argument('-b', '--batch_size', type=int, default=1000, help='block size')
    parser.add_argument('-bb', '--block_batch_size', type=int, default=1, help='block batch size')

    args = parser.parse_args()

    start_block = args.start_block_index if args.start_block_index >= 0 else None
    end_block = args.end_block_index if args.end_block_index >= 0 else None

    # TODO: add local run option (no s3)
    _job_path_prefix = get_job_path_prefix(
        job_name=args.job_name,
        start_block_index=start_block,
        end_block_index=end_block,
        num_nodes=args.nodes,
    )

    _start_block_index, _end_block_index = get_block_indexes(
        general_start_block_index=start_block,
        general_end_block_index=end_block,
        num_workers=args.nodes,
        worker_index=args.node_index,
    )

    # TODO: add types from args?
    entity_types = "block,transaction,log,contract,trace"
    # TODO: add parquet output, possibility for multiple outputs?
    postgres_output = generate_postgres_output()

    streaming(
        output=postgres_output,
        entity_types=entity_types,
        provider_uri=args.provider_uri,
        max_workers=args.max_workers,
        batch_size=args.batch_size,
        block_batch_size=args.block_batch_size,
        start_block=_start_block_index,
        end_block=_end_block_index,
        node_index=args.node_index,
        job_path_prefix=_job_path_prefix
    )
