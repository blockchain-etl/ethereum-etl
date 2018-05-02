import sys
import contextlib
import os


# https://stackoverflow.com/questions/17602878/how-to-handle-both-with-open-and-sys-stdout-nicely
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