import argparse

from ethereumetl.streaming.streaming import streaming
from hypernative.consts import NODE_PROVIDER, ENTITY_TYPES_DEFAULT
from hypernative.multi_node import get_block_indexes
from hypernative.output import generate_postgres_output
from hypernative.utils import get_job_path_prefix, natural_number

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='transaction backfill parsing')
    parser.add_argument('-name', '--job-name', type=str, default='default',
                        help='the name of the current job (used for recovery)')
    parser.add_argument('-s', '--start-block-index', type=natural_number, help='start block index')
    parser.add_argument('-e', '--end-block-index', type=natural_number, help='end block index')
    parser.add_argument('-n', '--nodes', type=int, default=0, help='number of nodes')
    parser.add_argument('-i', '--node-index', type=int, default=0, help='index of current node')
    parser.add_argument('-w', '--max-workers', type=int, default=5, help='number of workers per process')
    parser.add_argument('-provider', '--provider-uri', type=str, default=NODE_PROVIDER, help='provider uri')
    parser.add_argument('-b', '--batch-size', type=int, default=100, help='items per request')
    parser.add_argument('-bb', '--block-batch-size', type=int, default=1, help='blocks per batch')
    parser.add_argument('-o', '--output', type=str, default='postgres', help='output sinks')
    parser.add_argument(
        '-e',
        '--entity-types',
        type=str,
        default=','.join(ENTITY_TYPES_DEFAULT),
        help='The list of entity types to export'
    )
    args = parser.parse_args()

    _job_path_prefix = get_job_path_prefix(
        job_name=args.job_name,
        start_block_index=args.start_block_index,
        end_block_index=args.end_block_index,
        num_nodes=args.nodes,
    )

    # TODO: change multi processing by reading mini jobs from a queue instead of splitting the job into equal parts
    #       in the current way we get situations where one process takes much longer than another
    _start_block_index, _end_block_index = get_block_indexes(
        general_start_block_index=args.start_block_index,
        general_end_block_index=args.end_block_index,
        num_workers=args.nodes,
        worker_index=args.node_index,
    )

    streaming(
        output=generate_postgres_output(args.output),
        entity_types=args.entity_types,
        provider_uri=args.provider_uri,
        max_workers=args.max_workers,
        batch_size=args.batch_size,
        block_batch_size=args.block_batch_size,
        start_block=_start_block_index,
        end_block=_end_block_index,
        node_index=args.node_index,
        job_path_prefix=_job_path_prefix
    )
