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

RECEIPT_FIELDS_TO_EXPORT = [
    'transaction_hash',
    'transaction_index',
    'block_hash',
    'block_number',
    'cumulative_gas_used',
    'gas_used',
    'contract_address',
    'root',
    'status',
    'effective_gas_price',
    'l1_fee',
    'l1_gas_used',
    'l1_gas_price',
    'l1_fee_scalar',
    'blob_gas_price',
    'blob_gas_used'
]

LOG_FIELDS_TO_EXPORT = [
    'log_index',
    'transaction_hash',
    'transaction_index',
    'block_hash',
    'block_number',
    'address',
    'data',
    'topics'
]

def receipts_and_logs_item_exporter(receipts_output=None, logs_output=None):
    if is_gcs_path(receipts_output) or is_gcs_path(logs_output):
        # For GCS output
        # Get the bucket and path from either output
        output_path = receipts_output if receipts_output else logs_output
        bucket_name, _ = parse_gcs_path(output_path)
        
        # Get the blob names
        _, receipts_blob = parse_gcs_path(receipts_output) if receipts_output else (None, None)
        _, logs_blob = parse_gcs_path(logs_output) if logs_output else (None, None)
        
        item_type_to_filename_mapping = {}
        if receipts_output:
            item_type_to_filename_mapping['receipt'] = receipts_blob
        if logs_output:
            item_type_to_filename_mapping['log'] = logs_blob
            
        field_mapping = {
            'receipt': RECEIPT_FIELDS_TO_EXPORT,
            'log': LOG_FIELDS_TO_EXPORT
        }
        
        return create_gcs_exporter(
            output_path=f"gs://{bucket_name}",
            item_type_to_filename_mapping=item_type_to_filename_mapping,
            field_mapping=field_mapping
        )
    else:
        # File-based output
        return CompositeItemExporter(
            filename_mapping={
                'receipt': receipts_output,
                'log': logs_output
            },
            field_mapping={
                'receipt': RECEIPT_FIELDS_TO_EXPORT,
                'log': LOG_FIELDS_TO_EXPORT
            }
        )
