import logging
import time
from functools import wraps

from hypernative.consts import OFFSETS_BUCKET, ETHEREUM_NODE_OFFSETS_PREFIX


def timer_inner(func, logging_function, action, *args, **kwargs):
    processing_start_time = time.perf_counter()
    result = func(*args, **kwargs)
    logging_function('TIMER [{}] TOOK [{:.5f}] SECONDS'.format(
        action if action else func.__name__,
        time.perf_counter() - processing_start_time
    ))
    return result


def timer(function=None, logging_function=logging.info, action=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return timer_inner(func, logging_function, action, *args, **kwargs)
        return wrapper
    if function:
        return decorator(function)
    return decorator


def debug_timer(function=None, logging_function=logging.debug, action=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return timer_inner(func, logging_function, action, *args, **kwargs)
        return wrapper
    if function:
        return decorator(function)
    return decorator


def get_job_path_prefix(job_name, start_block_index, end_block_index, num_nodes):
    return f's3://{OFFSETS_BUCKET}/{ETHEREUM_NODE_OFFSETS_PREFIX}/' \
           f'{job_name}_{start_block_index}_{end_block_index}_n{num_nodes}'
