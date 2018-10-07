# MIT License
#
# Copyright (c) 2018 Evgeniy Filatov, evgeniyfilatov@gmail.com
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


from ethereumetl.jobs.exporters.composite_item_exporter import CompositeItemExporter

FIELDS_TO_EXPORT = [
    'block_number',
    'block_timestamp',
    'hash',
    'from_address',
    'to_address',
    'value',
    'contract_address',
    'input',
    'transaction_type',
    'gas',
    'gas_used',
    'trace_id',
    'is_error',
    'err_code',
]


def internal_transactions_item_exporter(internal_transactions_output):
    return CompositeItemExporter(
        filename_mapping={
            'internal_transaction': internal_transactions_output
        },
        field_mapping={
            'internal_transaction': FIELDS_TO_EXPORT
        }
    )
