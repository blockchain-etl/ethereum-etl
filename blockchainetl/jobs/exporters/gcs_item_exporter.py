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

from blockchainetl.exporters import GcsCsvItemExporter, GcsJsonLinesItemExporter
from blockchainetl.jobs.exporters.composite_item_exporter import CompositeItemExporter


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


class GcsItemExporter:

    def __init__(
            self,
            bucket,
            path='blocks',
            build_block_bundles_func=build_block_bundles):
        self.bucket = bucket
        self.path = normalize_path(path)
        self.build_block_bundles_func = build_block_bundles_func
        self.storage_client = storage.Client()

    def open(self):
        pass

    def export_items(self, items):
        block_bundles = self.build_block_bundles_func(items)

        for block_bundle in block_bundles:
            block = block_bundle.get('block')
            if block is None:
                raise ValueError('block_bundle must include the block field')
            block_number = block.get('number')
            if block_number is None:
                raise ValueError('block_bundle must include the block.number field')

            destination_blob_name = f'{self.path}/{block_number}.json'

            bucket = self.storage_client.bucket(self.bucket)
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_string(json.dumps(block_bundle))
            logging.info(f'Uploaded file gs://{self.bucket}/{destination_blob_name}')

    def close(self):
        pass


def normalize_path(p):
    if p is None:
        p = ''
    if p.startswith('/'):
        p = p[1:]
    if p.endswith('/'):
        p = p[:len(p) - 1]

    return p


def is_gcs_path(path):
    """Check if a path is a GCS path"""
    return path.startswith('gs://')


def parse_gcs_path(path):
    """Parse a GCS path into bucket and blob names"""
    path = path.replace('gs://', '')
    bucket_name = path.split('/')[0]
    blob_name = '/'.join(path.split('/')[1:])
    return bucket_name, blob_name


def create_gcs_exporter(output_path, item_type_to_filename_mapping, field_mapping=None, **kwargs):
    """Creates GCS exporters for each item type"""
    bucket_name, base_blob_path = parse_gcs_path(output_path)
    item_exporters = {}

    for item_type, filename in item_type_to_filename_mapping.items():
        blob_name = f"{base_blob_path}/{filename}"
        exporter_kwargs = kwargs.copy()
        
        # Add field mapping for this item type if available
        if field_mapping and item_type in field_mapping:
            exporter_kwargs['fields_to_export'] = field_mapping[item_type]

        if filename.endswith('.csv'):
            item_exporters[item_type] = GcsCsvItemExporter(
                bucket_name=bucket_name,
                blob_name=blob_name,
                **exporter_kwargs
            )
        else:
            item_exporters[item_type] = GcsJsonLinesItemExporter(
                bucket_name=bucket_name,
                blob_name=blob_name,
                **exporter_kwargs
            )

    return CompositeItemExporter(item_exporters=item_exporters)
