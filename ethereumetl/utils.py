import sys
import contextlib
import os


# https://stackoverflow.com/questions/17602878/how-to-handle-both-with-open-and-sys-stdout-nicely
import eth_utils


@contextlib.contextmanager
def smart_open(filename=None, mode='w', binary=False):
    is_file = filename and filename != '-'
    full_mode = mode + ('b' if binary else '')
    if is_file:
        fh = open(filename, full_mode)
    else:
        fd = sys.stdout.fileno() if mode == 'w' else sys.stdin.fileno()
        fh = os.fdopen(fd, full_mode)

    try:
        yield fh
    finally:
        if is_file:
            fh.close()


def hex_to_dec(hex_string):
    if hex_string is None:
        return None
    try:
        return int(hex_string, 16)
    except ValueError:
        print("Not a hex string %s" % hex_string)
        return hex_string


def chunk_string(string, length):
    return (string[0 + i:length + i] for i in range(0, len(string), length))


def batch_readlines(file, batch_size):
    current_batch_size = 0
    batch = []
    for line in file:
        batch.append(line)
        current_batch_size += 1
        if current_batch_size == batch_size:
            yield batch
            batch = []
            current_batch_size = 0
    if current_batch_size != 0:
        yield batch


def to_normalized_address(address):
    if address is None or not isinstance(address, str):
        return address
    return address.lower()

