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
from google.cloud import storage
from io import StringIO, BytesIO

def is_gcs_path(path):
    """Check if a path is a GCS path"""
    return path.startswith('gs://')

def parse_gcs_path(path):
    """Parse a GCS path into bucket and blob names"""
    path = path.replace('gs://', '')
    bucket_name = path.split('/')[0]
    blob_name = '/'.join(path.split('/')[1:])
    return bucket_name, blob_name

# https://stackoverflow.com/questions/17602878/how-to-handle-both-with-open-and-sys-stdout-nicely
@contextlib.contextmanager
def smart_open(filename=None, mode='w', binary=False, create_parent_dirs=True):
    """Opens a file or stdout in a smart way."""
    is_file = filename and filename != '-'

    if is_file:
        if is_gcs_path(filename):
            fh = get_gcs_file_handle(filename, mode, binary)
        else:
            if create_parent_dirs:
                os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
            fh = get_file_handle(filename, mode=mode, binary=binary)
    elif binary:
        fh = sys.stdout.buffer
    else:
        fh = sys.stdout

    try:
        yield fh
    finally:
        if is_file:
            fh.close()

def get_gcs_file_handle(path, mode='r', binary=False):
    """Get a file-like object for reading from or writing to GCS."""
    client = storage.Client()
    bucket_name, blob_name = parse_gcs_path(path)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    if 'r' in mode:  # Reading
        if binary:
            content = blob.download_as_bytes()
            return BytesIO(content)
        else:
            content = blob.download_as_text()
            return StringIO(content)
    else:  # Writing
        if binary:
            return GCSBinaryUploadStream(blob)
        else:
            return GCSUploadStream(blob)

def get_file_handle(filename, mode='w', binary=False, create_parent_dirs=True):
    """Get a file handle for writing."""
    if create_parent_dirs:
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
    
    if binary:
        mode = mode.replace('w', 'wb').replace('r', 'rb')
    
    return open(filename, mode)

def close_silently(file_handle):
    """Close a file handle silently."""
    if file_handle is None:
        return
    
    try:
        file_handle.close()
    except Exception as e:
        logging.warning(f'Error closing file handle: {e}')

class GCSUploadStream:
    """A file-like object for uploading to GCS."""
    def __init__(self, blob):
        self.blob = blob
        self.buffer = StringIO()

    def write(self, data):
        self.buffer.write(data)

    def close(self):
        self.blob.upload_from_string(self.buffer.getvalue())
        self.buffer.close()

class GCSBinaryUploadStream:
    """A file-like object for uploading binary data to GCS."""
    def __init__(self, blob):
        self.blob = blob
        self.buffer = BytesIO()

    def write(self, data):
        self.buffer.write(data)

    def close(self):
        self.blob.upload_from_file(self.buffer, rewind=True)
        self.buffer.close()

class NoopFile:
    """A no-op file object that does nothing."""
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
