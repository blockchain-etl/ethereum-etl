# MIT License
#
# Copyright (c) 2020 Evgeny Medvedev, evge.medvedev@gmail.com
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

import json
import logging
from collections import defaultdict

from google.cloud import storage


class GcsItemExporter:

    def __init__(
            self,
            bucket):
        self.bucket = bucket
        self.storage_client = storage.Client()

    def open(self):
        pass

    def export_items(self, items):
        block_bundles = build_block_bundles(items)

        for block_bundle in block_bundles:
            block_number = block_bundle['block']['number']
            destination_blob_name = f'blocks/{block_number}.json'

            bucket = self.storage_client.bucket(self.bucket)
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_string(json.dumps(block_bundle))
            logging.info(f'Uploaded file gs://{self.bucket}/{destination_blob_name}')

    def close(self):
        pass


def build_block_bundles(items):
    blocks = defaultdict(list)
    transactions = defaultdict(list)
    logs = defaultdict(list)
    token_transfers = defaultdict(list)
    traces = defaultdict(list)
    for item in items:
        item_type = item.get('type')
        if item_type == 'block':
            blocks[item.get('number')].append(item)
        elif item_type == 'transaction':
            transactions[item.get('block_number')].append(item)
        elif item_type == 'log':
            logs[item.get('block_number')].append(item)
        elif item_type == 'token_transfer':
            token_transfers[item.get('block_number')].append(item)
        elif item_type == 'trace':
            traces[item.get('block_number')].append(item)
        else:
            logging.info(f'Skipping item with type {item_type}')

    block_bundles = []
    for block_number in sorted(blocks.keys()):
        if len(blocks[block_number]) != 1:
            raise ValueError(f'There must be a single block for a given block number, was {len(blocks[block_number])} for block number {block_number}')
        block_bundles.append({
            'block': blocks[block_number][0],
            'transactions': transactions[block_number],
            'logs': logs[block_number],
            'token_transfers': token_transfers[block_number],
            'traces': traces[block_number],
        })

    return block_bundles
