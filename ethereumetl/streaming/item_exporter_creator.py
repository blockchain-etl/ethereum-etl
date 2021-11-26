#  MIT License
#
#  Copyright (c) 2020 Evgeny Medvedev, evge.medvedev@gmail.com
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

from blockchainetl.jobs.exporters.console_item_exporter import ConsoleItemExporter
from blockchainetl.jobs.exporters.s3_item_exporter import S3ItemExporter


def create_item_exporter(output, **kwargs):
    item_exporter_type = determine_item_exporter_type(output)
    if item_exporter_type == ItemExporterType.PUBSUB:
        from blockchainetl.jobs.exporters.google_pubsub_item_exporter import GooglePubSubItemExporter
        item_exporter = GooglePubSubItemExporter(item_type_to_topic_mapping={
            'block': output + '.blocks',
            'transaction': output + '.transactions',
            'log': output + '.logs',
            'token_transfer': output + '.token_transfers',
            'trace': output + '.traces',
            'contract': output + '.contracts',
            'token': output + '.tokens',
        })
    elif item_exporter_type == ItemExporterType.POSTGRES:
        from blockchainetl.jobs.exporters.postgres_item_exporter import PostgresItemExporter
        from blockchainetl.streaming.postgres_utils import create_insert_statement_for_table
        from blockchainetl.jobs.exporters.converters.unix_timestamp_item_converter import UnixTimestampItemConverter
        from blockchainetl.jobs.exporters.converters.int_to_decimal_item_converter import IntToDecimalItemConverter
        from blockchainetl.jobs.exporters.converters.list_field_item_converter import ListFieldItemConverter
        from ethereumetl.streaming.postgres_tables import BLOCKS, TRANSACTIONS, LOGS, TOKEN_TRANSFERS, TRACES

        item_exporter = PostgresItemExporter(
            output, item_type_to_insert_stmt_mapping={
                'block': create_insert_statement_for_table(BLOCKS),
                'transaction': create_insert_statement_for_table(TRANSACTIONS),
                'log': create_insert_statement_for_table(LOGS),
                'token_transfer': create_insert_statement_for_table(TOKEN_TRANSFERS),
                'trace': create_insert_statement_for_table(TRACES),
            },
            converters=[UnixTimestampItemConverter(), IntToDecimalItemConverter(),
                        ListFieldItemConverter('topics', 'topic', fill=6)])
    elif item_exporter_type == ItemExporterType.CONSOLE:
        item_exporter = ConsoleItemExporter()
    elif item_exporter_type == ItemExporterType.S3:
        from blockchainetl.jobs.exporters.converters.unix_timestamp_item_converter import UnixTimestampItemConverter
        from blockchainetl.jobs.exporters.converters.int_to_decimal_item_converter import IntToDecimalItemConverter
        from blockchainetl.jobs.exporters.converters.list_field_item_converter import ListFieldItemConverter
        item_exporter = S3ItemExporter(bucket=output.split('//')[-1], converters=[UnixTimestampItemConverter()], environment=kwargs.get('environment','dev'), chain=kwargs.get('chain', 'ethereum')
                , filename_mapping={'block': 'blocks.csv',
            'transaction': 'transactions.csv',
            'log': 'logs.json',
            'token_transfer': 'token_transfers.csv',
            'trace': 'traces.csv',
            'contract':  'contracts.json',
            'token': 'tokens.json'})
    else:
        raise ValueError('Unable to determine item exporter type for output ' + output)

    return item_exporter


def determine_item_exporter_type(output):
    if output is not None and output.startswith('projects'):
        return ItemExporterType.PUBSUB
    elif output is not None and output.startswith('postgresql'):
        return ItemExporterType.POSTGRES
    elif output is not None and output.startswith('s3'):
        return ItemExporterType.S3
    elif output is None or output == 'console':
        return ItemExporterType.CONSOLE
    else:
        return ItemExporterType.UNKNOWN


class ItemExporterType:
    PUBSUB = 'pubsub'
    POSTGRES = 'postgres'
    CONSOLE = 'console'
    S3 = 's3'
    UNKNOWN = 'unknown'
