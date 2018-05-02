import sys
import contextlib


# https://stackoverflow.com/questions/17602878/how-to-handle-both-with-open-and-sys-stdout-nicely
@contextlib.contextmanager
def smart_open(filename=None, binary=False):
    if filename and filename != '-':
        fh = open(filename, 'w' + ('b' if binary else ''))
    else:
        fh = sys.stdout.buffer if binary else sys.stdout

    try:
        yield fh
    finally:
        if fh is not (sys.stdout.buffer if binary else sys.stdout):
            fh.close()


def hex_to_dec(hex_string):
    if hex_string is None:
        return None
    try:
        return int(hex_string, 16)
    except ValueError:
        print("Not a hex string %s" % hex_string)
        return hex_string