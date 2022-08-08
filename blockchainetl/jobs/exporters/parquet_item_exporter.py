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
from dataclasses import dataclass, field
from typing import List, Dict

import pandas as pd
import awswrangler as wr

from blockchainetl.jobs.exporters.converters.composite_item_converter import CompositeItemConverter
from hypernative.consts import ETHEREUM_ETL_BUCKET, ETHEREUM_ETL_ATHENA_DB_NAME


@dataclass
class ParquetExporterTableArgs:
    s3_prefix: str
    table_name: str
    schema: Dict[str, str]
    to_drop_columns: List[str] = field(default_factory=lambda: ['type', 'item_id', 'item_timestamp'])


class ParquetItemExporter:

    def __init__(self, connection_url, item_type_to_parquet_export_args_mapping, converters=()):
        self.connection_url = connection_url
        self.item_type_to_parquet_export_args_mapping: Dict[str, ParquetExporterTableArgs] = \
            item_type_to_parquet_export_args_mapping
        self.converter = CompositeItemConverter(converters)

    def open(self):
        pass

    def export_items(self, items):
        items_grouped_by_type = group_by_item_type(items)

        for item_type, parquet_export_args in self.item_type_to_parquet_export_args_mapping.items():
            item_group = items_grouped_by_type.get(item_type)
            if item_group:
                converted_items = list(self.convert_items(item_group))
                df = pd.DataFrame.from_dict(converted_items)
                wr.s3.to_parquet(
                    df=df.drop(parquet_export_args.to_drop_columns, axis=1),
                    path=f"s3://{ETHEREUM_ETL_BUCKET}/{parquet_export_args.s3_prefix}/",
                    dataset=True,
                    partition_cols=['date'],
                    mode="append",
                    database=ETHEREUM_ETL_ATHENA_DB_NAME,
                    table=parquet_export_args.table_name,
                    dtype=parquet_export_args.schema
                )

    def convert_items(self, items):
        for item in items:
            yield self.converter.convert_item(item)

    def close(self):
        pass


def group_by_item_type(items):
    result = collections.defaultdict(list)
    for item in items:
        result[item.get('type')].append(item)

    return result
