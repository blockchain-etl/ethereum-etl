import collections
import logging
from typing import List
from urllib.parse import urlparse, parse_qs
from dataclasses import dataclass

from clickhouse_connect.driver.exceptions import DatabaseError
from clickhouse_connect.driver.models import ColumnDef

import clickhouse_connect


@dataclass
class Table:
    column_names: List[str]
    column_types: List[str]


MIN_INSERT_BATCH_SIZE = 1000


class ClickHouseItemExporter:

    def __init__(self, connection_url, item_type_to_table_mapping):
        parsed = urlparse(connection_url)
        self.username = parsed.username
        self.password = parsed.password
        self.host = parsed.hostname
        self.port = parsed.port
        self.database = parsed.path[1:].split('/')[0] if parsed.path else 'default'
        self.settings = dict(parse_qs(parsed.query))
        self.item_type_to_table_mapping = item_type_to_table_mapping
        self.connection = self.create_connection()
        self.tables = {}
        self.cached_batches = {}
        ## for each time grab the schema to save a prefetch of the columns on each insert
        for table in self.item_type_to_table_mapping.values():
            try:
                describe_result = self.connection.query(f'DESCRIBE TABLE {self.database}.{table}')
                column_defs = [ColumnDef(**row) for row in describe_result.named_results()
                               if row['default_type'] not in ('ALIAS', 'MATERIALIZED')]
                column_names = [cd.name for cd in column_defs]
                column_types = [cd.ch_type for cd in column_defs]
                self.tables[table] = Table(column_names, column_types)
                self.cached_batches[table] = []
            except DatabaseError as de:
                # this may not be critical since the user may not be exporting the type and hence the table likely
                # won't exist
                logging.warning('Unable to read columns for table "{}". This column will not be exported.'.format(table))
                logging.debug(de)
                pass

    def open(self):
        pass

    def export_items(self, items):
        items_grouped_by_table = self.group_items_by_table(items)
        for item_type, table in self.item_type_to_table_mapping.items():
            table_data = items_grouped_by_table.get(table)
            if table_data:
                cached = self.cached_batches[table]
                batch = cached + table_data
                if len(batch) >= MIN_INSERT_BATCH_SIZE:
                    logging.info('Flushing batch for "{}" with {} items.'.format(item_type, len(batch)))
                    self.connection.insert(table, data=table_data, column_names=self.tables[table].column_names,
                                           column_types=self.tables[table].column_types, database=self.database)
                    self.cached_batches[table] = []
                else:
                    # insufficient size, so cache
                    logging.debug(
                        'Batch for "{}" is too small to be flushed ({}<{}), caching.'.format(item_type, len(batch),
                                                                                             MIN_INSERT_BATCH_SIZE))
                    self.cached_batches[table] = batch

    def convert_items(self, items):
        for item in items:
            yield self.converter.convert_item(item)

    def create_connection(self):
        return clickhouse_connect.create_client(host=self.host, port=self.port, username=self.username,
                                                password=self.password, database=self.database,
                                                settings=self.settings)

    def close(self):
        # clear the cache
        logging.info("Flushing remaining batches")
        for table, batch in self.cached_batches.items():
            self.connection.insert(table, data=batch, column_names=self.tables[table].column_names,
                                   column_types=self.tables[table].column_types, database=self.database)
        self.connection.close()

    def group_items_by_table(self, items):
        results = collections.defaultdict(list)
        for item in items:
            type = item.get('type')
            if type in self.item_type_to_table_mapping:
                table = self.item_type_to_table_mapping[type]
                if table not in self.tables:
                    logging.error('Table "{}" does not exist. Type "{}" cannot be exported.'.format(table, type))
                result = []
                # only insert the columns which we have in the database
                for column in self.tables[table].column_names:
                    result.append(item.get(column))
                results[table].append(result)
            else:
                logging.warning('ClickHouse exporter ignoring {} items as type is not currently supported.'.format(type))
        return results
