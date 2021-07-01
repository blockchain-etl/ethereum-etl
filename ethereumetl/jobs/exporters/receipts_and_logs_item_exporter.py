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
    'effective_gas_price'
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
