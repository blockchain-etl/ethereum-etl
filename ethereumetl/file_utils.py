import contextlib
import os
import pathlib
import sys


# https://stackoverflow.com/questions/17602878/how-to-handle-both-with-open-and-sys-stdout-nicely
@contextlib.contextmanager
def smart_open(filename=None, mode='w', binary=False, create_parent_dirs=True):
    fh = get_file_handle(filename, mode, binary, create_parent_dirs)

    try:
        yield fh
    finally:
        fh.close()


def get_file_handle(filename, mode='w', binary=False, create_parent_dirs=True):
    if create_parent_dirs and filename is not None:
        dirname = os.path.dirname(filename)
        pathlib.Path(dirname).mkdir(parents=True, exist_ok=True)
    full_mode = mode + ('b' if binary else '')
    is_file = filename and filename != '-'
    if is_file:
        fh = open(filename, full_mode)
    elif filename == '-':
        fd = sys.stdout.fileno() if mode == 'w' else sys.stdin.fileno()
        fh = os.fdopen(fd, full_mode)
    else:
        fh = NoopFile()
    return fh


def close_silently(file_handle):
    if file_handle is None:
        pass
    try:
        file_handle.close()
    except OSError:
        pass


class NoopFile:
    def __enter__(self):
        pass

    def __exit__(self):
        pass

    def readable(self):
        pass

    def writable(self):
        pass

    def seekable(self):
        pass

    def close(self):
        pass

    def write(self, bytes):
        pass
