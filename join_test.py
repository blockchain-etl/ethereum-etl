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


import argparse
import itertools
from collections import defaultdict

from ethereumetl.logging_utils import logging_basic_config

logging_basic_config()

parser = argparse.ArgumentParser(description='')

args = parser.parse_args()


def join(left, right, join_fields, left_fields, right_fields):
    left_join_field, right_join_field = join_fields

    def field_list_to_dict(field_list):
        result_dict = {}
        for field in field_list:
            if isinstance(field, tuple):
                result_dict[field[0]] = field[1]
            else:
                result_dict[field] = field
        return result_dict

    left_fields_as_dict = field_list_to_dict(left_fields)
    right_fields_as_dict = field_list_to_dict(right_fields)

    left_map = defaultdict(list)
    for item in left: left_map[item[left_join_field]].append(item)

    right_map = defaultdict(list)
    for item in right: right_map[item[right_join_field]].append(item)

    assert left_map.keys() == right_map.keys()

    for key in left_map.keys():
        for left_item, right_item in itertools.product(left_map[key], right_map[key]):
            result_item = {}
            for src_field, dst_field in left_fields_as_dict.items():
                result_item[dst_field] = left_item.get(src_field)
            for src_field, dst_field in right_fields_as_dict.items():
                result_item[dst_field] = right_item.get(src_field)

            yield result_item


blocks = [
    {'number': 1, 'timestamp': '0x11'}
]

transactions = [
    {'block_number': 1, 'transaction_hash': '0x22'},
    {'block_number': 1, 'transaction_hash': '0x33'}
]

receipts = [
    {'transaction_hash': '0x22', 'gas_used': 1},
    {'transaction_hash': '0x33', 'gas_used': 2}
]

result = join(blocks, transactions, ('number', 'block_number'),
              [
                  ('number', 'block_number'),
                  ('timestamp', 'block_timestamp')
              ],
              [
                  'transaction_hash'
              ])

result = join(result, receipts, ('transaction_hash', 'transaction_hash'),
              [
                  'block_number',
                  'block_timestamp',
                  'transaction_hash',
              ],
              [
                  'gas_used'
              ])

for i in result:
    print(i)