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


from ethereumetl.jobs.exporters.composite_item_exporter import CompositeItemExporter

PENDING_TRANSACTION_FIELDS_TO_EXPORT = [
    'hash',
    'nonce',
    'from_address',
    'to_address',
    'value',
    'gas',
    'gas_price',
    'input',
    'timestamp'
]


def pending_transactions_item_exporter(pending_transactions_output=None):
    return CompositeItemExporter(
        filename_mapping={
            'pending_transaction': pending_transactions_output
        },
        field_mapping={
            'pending_transaction': PENDING_TRANSACTION_FIELDS_TO_EXPORT
        }
    )
