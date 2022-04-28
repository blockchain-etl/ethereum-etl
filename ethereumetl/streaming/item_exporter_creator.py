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
from blockchainetl.jobs.exporters.multi_item_exporter import MultiItemExporter


def create_item_exporters(outputs):
    split_outputs = [output.strip() for output in outputs.split(',')] if outputs else ['console']

    item_exporters = [create_item_exporter(output) for output in split_outputs]
    return MultiItemExporter(item_exporters)


def create_item_exporter(output):
    item_exporter_type = determine_item_exporter_type(output)
    if item_exporter_type == ItemExporterType.PUBSUB:
        from blockchainetl.jobs.exporters.google_pubsub_item_exporter import GooglePubSubItemExporter
        enable_message_ordering = 'sorted' in output or 'ordered' in output
        item_exporter = GooglePubSubItemExporter(
            item_type_to_topic_mapping={
                'block': output + '.blocks',
                'transaction': output + '.transactions',
                'log': output + '.logs',
                'token_transfer': output + '.token_transfers',
                'trace': output + '.traces',
                'contract': output + '.contracts',
                'token': output + '.tokens',
            },
            message_attributes=('item_id', 'item_timestamp'),
            batch_max_bytes=1024 * 1024 * 5,
            batch_max_latency=2,
            batch_max_messages=1000,
            enable_message_ordering=enable_message_ordering)
    elif item_exporter_type == ItemExporterType.POSTGRES:
        from blockchainetl.jobs.exporters.postgres_item_exporter import PostgresItemExporter
        from blockchainetl.streaming.postgres_utils import create_insert_statement_for_table
        from blockchainetl.jobs.exporters.converters.unix_timestamp_item_converter import UnixTimestampItemConverter
        from blockchainetl.jobs.exporters.converters.int_to_decimal_item_converter import IntToDecimalItemConverter
        from blockchainetl.jobs.exporters.converters.list_field_item_converter import ListFieldItemConverter
        from ethereumetl.streaming.postgres_tables import BLOCKS, TRANSACTIONS, LOGS, TOKEN_TRANSFERS, TRACES, TOKENS, CONTRACTS

        item_exporter = PostgresItemExporter(
            output, item_type_to_insert_stmt_mapping={
                'block': create_insert_statement_for_table(BLOCKS),
                'transaction': create_insert_statement_for_table(TRANSACTIONS),
                'log': create_insert_statement_for_table(LOGS),
                'token_transfer': create_insert_statement_for_table(TOKEN_TRANSFERS),
                'trace': create_insert_statement_for_table(TRACES),
                'token': create_insert_statement_for_table(TOKENS),
                'contract': create_insert_statement_for_table(CONTRACTS),
            },
            converters=[UnixTimestampItemConverter(), IntToDecimalItemConverter(),
                        ListFieldItemConverter('topics', 'topic', fill=4)])
    elif item_exporter_type == ItemExporterType.GCS:
        from blockchainetl.jobs.exporters.gcs_item_exporter import GcsItemExporter
        bucket, path = get_bucket_and_path_from_gcs_output(output)
        item_exporter = GcsItemExporter(bucket=bucket, path=path)
    elif item_exporter_type == ItemExporterType.CONSOLE:
        item_exporter = ConsoleItemExporter()
    elif item_exporter_type == ItemExporterType.KAFKA:
        from blockchainetl.jobs.exporters.kafka_exporter import KafkaItemExporter
        item_exporter = KafkaItemExporter(output, item_type_to_topic_mapping={
            'block': 'blocks',
            'transaction': 'transactions',
            'log': 'logs',
            'token_transfer': 'token_transfers',
            'trace': 'traces',
            'contract': 'contracts',
            'token': 'tokens',
        })

    else:
        raise ValueError('Unable to determine item exporter type for output ' + output)

    return item_exporter


def get_bucket_and_path_from_gcs_output(output):
    output = output.replace('gs://', '')
    bucket_and_path = output.split('/', 1)
    bucket = bucket_and_path[0]
    if len(bucket_and_path) > 1:
        path = bucket_and_path[1]
    else:
        path = ''
    return bucket, path


def determine_item_exporter_type(output):
    if output is not None and output.startswith('projects'):
        return ItemExporterType.PUBSUB
    if output is not None and output.startswith('kafka'):
        return ItemExporterType.KAFKA
    elif output is not None and output.startswith('postgresql'):
        return ItemExporterType.POSTGRES
    elif output is not None and output.startswith('gs://'):
        return ItemExporterType.GCS
    elif output is None or output == 'console':
        return ItemExporterType.CONSOLE
    else:
        return ItemExporterType.UNKNOWN


class ItemExporterType:
    PUBSUB = 'pubsub'
    POSTGRES = 'postgres'
    GCS = 'gcs'
    CONSOLE = 'console'
    KAFKA = 'kafka'
    UNKNOWN = 'unknown'
