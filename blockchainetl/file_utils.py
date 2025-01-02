# MIT License
#
# Copyright (c) 2018 Evgeny Medvedev, evge.medvedev@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import contextlib
import os
import pathlib
import sys
import logging


# https://stackoverflow.com/questions/17602878/how-to-handle-both-with-open-and-sys-stdout-nicely
@contextlib.contextmanager
def smart_open(filename=None, mode='w', binary=False, create_parent_dirs=True):
    fh = get_file_handle(filename, mode, binary, create_parent_dirs)

    try:
        yield fh
    finally:
        fh.close()


def get_file_handle(filename, binary=False):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    full_path = os.path.abspath(filename)
    mode = 'wb' if binary else 'w'
    return open(full_path, mode)


def close_silently(file_handle):
    if file_handle is None:
        return
    
    try:
        file_handle.close()
    except Exception as e:
        logging.warning(f'Error closing file handle: {e}')


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
