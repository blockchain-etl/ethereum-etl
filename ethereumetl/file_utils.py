import sys
import contextlib
import os


# https://stackoverflow.com/questions/17602878/how-to-handle-both-with-open-and-sys-stdout-nicely
@contextlib.contextmanager
def smart_open(filename=None, mode='w', binary=False):
    full_mode = mode + ('b' if binary else '')
    is_file = filename and filename != '-'
    if is_file:
        fh = open(filename, full_mode)
    elif filename == '-':
        fd = sys.stdout.fileno() if mode == 'w' else sys.stdin.fileno()
        fh = os.fdopen(fd, full_mode)
    else:
        fh = NoopFile()

    try:
        yield fh
    finally:
        if is_file:
            fh.close()


class NoopFile:
    def readable(self):
        pass

    def writable(self):
        pass

    def seekable(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self):
        pass

    def close(self):
        pass

    def write(self):
        pass
