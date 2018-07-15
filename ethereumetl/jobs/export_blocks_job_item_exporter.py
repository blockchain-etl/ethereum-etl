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

BLOCK_FIELDS_TO_EXPORT = [
    'block_number',
    'block_hash',
    'block_parent_hash',
    'block_nonce',
    'block_sha3_uncles',
    'block_logs_bloom',
    'block_transactions_root',
    'block_state_root',
    'block_miner',
    'block_difficulty',
    'block_total_difficulty',
    'block_size',
    'block_extra_data',
    'block_gas_limit',
    'block_gas_used',
    'block_timestamp',
    'block_transaction_count'
]

TRANSACTION_FIELDS_TO_EXPORT = [
    'tx_hash',
    'tx_nonce',
    'tx_block_hash',
    'tx_block_number',
    'tx_index',
    'tx_from',
    'tx_to',
    'tx_value',
    'tx_gas',
    'tx_gas_price',
    'tx_input'
]


def export_blocks_job_item_exporter(blocks_output=None, transactions_output=None):
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
