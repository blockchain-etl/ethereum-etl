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


from ethereumetl.jobs.composite_item_exporter import CompositeItemExporter

RECEIPT_FIELDS_TO_EXPORT = [
    'receipt_transaction_hash',
    'receipt_transaction_index',
    'receipt_block_hash',
    'receipt_block_number',
    'receipt_cumulative_gas_used',
    'receipt_gas_used',
    'receipt_contract_address',
    'receipt_root',
    'receipt_status'
]

LOG_FIELDS_TO_EXPORT = [
    'log_index',
    'log_transaction_hash',
    'log_transaction_index',
    'log_block_hash',
    'log_block_number',
    'log_address',
    'log_data',
    'log_topics'
]


def export_receipts_job_item_exporter(receipts_output=None, logs_output=None):
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
