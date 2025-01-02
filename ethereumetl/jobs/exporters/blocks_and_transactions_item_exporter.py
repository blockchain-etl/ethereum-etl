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


from blockchainetl.jobs.exporters.composite_item_exporter import CompositeItemExporter
from blockchainetl.jobs.exporters.gcs_item_exporter import create_gcs_exporter, is_gcs_path, parse_gcs_path
from blockchainetl.file_utils import get_file_handle, close_silently
import os

BLOCK_FIELDS_TO_EXPORT = [
    'number',
    'hash',
    'parent_hash',
    'nonce',
    'sha3_uncles',
    'logs_bloom',
    'transactions_root',
    'state_root',
    'receipts_root',
    'miner',
    'difficulty',
    'total_difficulty',
    'size',
    'extra_data',
    'gas_limit',
    'gas_used',
    'timestamp',
    'transaction_count',
    'base_fee_per_gas',
    'withdrawals_root',
    'withdrawals',
    'blob_gas_used',
    'excess_blob_gas'
]

TRANSACTION_FIELDS_TO_EXPORT = [
    'hash',
    'nonce',
    'block_hash',
    'block_number',
    'transaction_index',
    'from_address',
    'to_address',
    'value',
    'gas',
    'gas_price',
    'input',
    'block_timestamp',
    'max_fee_per_gas',
    'max_priority_fee_per_gas',
    'transaction_type',
    'max_fee_per_blob_gas',
    'blob_versioned_hashes'
]


def create_blocks_and_transactions_exporter(blocks_output, transactions_output):
    if is_gcs_path(blocks_output):
        # For GCS output
        # Get the bucket and path from the blocks output
        bucket_name, blocks_blob = parse_gcs_path(blocks_output)
        _, transactions_blob = parse_gcs_path(transactions_output)
        
        item_type_to_filename_mapping = {
            'block': blocks_blob,
            'transaction': transactions_blob
        }
        field_mapping = {
            'block': BLOCK_FIELDS_TO_EXPORT,
            'transaction': TRANSACTION_FIELDS_TO_EXPORT
        }
        return create_gcs_exporter(
            output_path=f"gs://{bucket_name}",
            item_type_to_filename_mapping=item_type_to_filename_mapping,
            field_mapping=field_mapping
        )
    else:
        # File-based output
        return _create_file_based_exporter(blocks_output, transactions_output)

def _create_file_based_exporter(blocks_output, transactions_output):
    return CompositeItemExporter(
        filename_mapping={
            'block': blocks_output,
            'transaction': transactions_output
        },
        field_mapping={
            'block': BLOCK_FIELDS_TO_EXPORT,
            'transaction': TRANSACTION_FIELDS_TO_EXPORT
        }
    )
