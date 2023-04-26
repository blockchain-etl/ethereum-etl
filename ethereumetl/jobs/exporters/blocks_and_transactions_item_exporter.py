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

BLOCK_FIELDS_TO_EXPORT = [
    'block_number',
    'block_hash',
    'new_root',
    'parent_hash',
    'sequencer_address',
    'status',
    'timestamp'
]

TRANSACTION_FIELDS_TO_EXPORT = [
    'block_hash',
    'block_number',
    'block_timestamp',
    'class_hash',
    'constructor_calldata',
    'contract_address_salt',
    'transaction_hash',
    'transaction_type',
    'version',
    'calldata',
    'contract_address',
    'entry_point_selector',
    'max_fee',
    'nonce',
    'signature',
    'sender_address'
]


def blocks_and_transactions_item_exporter(blocks_output=None, transactions_output=None):
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
