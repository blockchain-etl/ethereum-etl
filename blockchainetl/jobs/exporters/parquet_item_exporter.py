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

import collections

import pandas as pd

from blockchainetl.jobs.exporters.converters.composite_item_converter import CompositeItemConverter


class ParquetItemExporter:

    def __init__(self, connection_url, item_type_to_insert_stmt_mapping, converters=(), print_sql=True):
        self.connection_url = connection_url
        self.item_type_to_insert_stmt_mapping = item_type_to_insert_stmt_mapping
        self.converter = CompositeItemConverter(converters)
        self.print_sql = print_sql

        # self.engine = self.create_engine()

    def open(self):
        pass

    def export_items(self, items):
        items_grouped_by_type = group_by_item_type(items)

        BASE_PATH = "s3://hypernative-srulik/parq-test"
        BASE_PATH = "/Users/asrulik/hypernative-srulik/parq-test"

        for item_type, insert_stmt in self.item_type_to_insert_stmt_mapping.items():
            item_group = items_grouped_by_type.get(item_type)
            if item_group:
                import pyarrow.parquet as pq
                # connection = self.engine.connect()
                converted_items = list(self.convert_items(item_group))
                df = pd.DataFrame.from_dict(converted_items)
                df.drop(['type', 'item_id', 'item_timestamp'], axis=1).to_parquet(f"{BASE_PATH}/{df['type'][0]}/1")
                print(df.dtypes)
                p_df = pd.read_parquet(f"{BASE_PATH}/{df['type'][0]}/1")
                print(p_df.dtypes)
                sc = pq.read_metadata(f"{BASE_PATH}/{df['type'][0]}/1")
                i = 1
                # connection.execute(insert_stmt, converted_items)
                # TODO: format and write to s3

    def convert_items(self, items):
        for item in items:
            yield self.converter.convert_item(item)

    # def create_engine(self):
        # engine = create_engine(self.connection_url, echo=self.print_sql, pool_recycle=3600)
        # return engine

    def close(self):
        pass


def group_by_item_type(items):
    result = collections.defaultdict(list)
    for item in items:
        result[item.get('type')].append(item)

    return result
