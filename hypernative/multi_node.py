import math


def get_block_indexes(general_start_block_index, general_end_block_index, num_workers, worker_index):
    if num_workers == 0:
        return general_start_block_index, general_end_block_index

    blocks_per_node = math.ceil((general_end_block_index - general_start_block_index) / num_workers)
    start_block_index = general_start_block_index + worker_index * blocks_per_node

    if worker_index < num_workers - 1:
        return start_block_index, general_start_block_index + (worker_index + 1) * blocks_per_node
    else:
        return start_block_index, general_end_block_index
