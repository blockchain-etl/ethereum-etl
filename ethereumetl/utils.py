import sys
import contextlib
import os


# https://stackoverflow.com/questions/17602878/how-to-handle-both-with-open-and-sys-stdout-nicely
@contextlib.contextmanager
def smart_open(filename=None, binary=False):
    is_file = filename and filename != '-'
    if is_file:
        fh = open(filename, 'w' + ('b' if binary else ''))
    else:
        fh = os.fdopen(sys.stdout.fileno(), 'w' + ('b' if binary else ''))

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