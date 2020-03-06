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


def create_item_exporter(output):
    if output is not None and output.startswith('projects'):
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
    elif output is not None and output.startswith('postgresql'):
        from blockchainetl.jobs.exporters.postgres_item_exporter import PostgresItemExporter
        from blockchainetl.streaming.postgres_utils import create_insert_statement_for_table
        from blockchainetl.jobs.exporters.converters.unix_timestamp_item_converter  import UnixTimestampItemConverter
        from blockchainetl.jobs.exporters.converters.int_to_decimal_item_converter  import IntToDecimalItemConverter
        from blockchainetl.jobs.exporters.converters.list_item_converter import ListItemConverter
        from ethereumetl.streaming.postgres_tables import BLOCKS, TRANSACTIONS, LOGS, TOKEN_TRANSFERS, TRACES

        item_exporter = PostgresItemExporter(
            output, item_type_to_insert_stmt_mapping={
                'block': create_insert_statement_for_table(BLOCKS),
                'transaction': create_insert_statement_for_table(TRANSACTIONS),
                'log': create_insert_statement_for_table(LOGS),
                'token_transfer': create_insert_statement_for_table(TOKEN_TRANSFERS),
                'traces': create_insert_statement_for_table(TRACES),
            },
            converters=[UnixTimestampItemConverter(), IntToDecimalItemConverter(),
                        ListItemConverter('topics', 'topic', fill=4)])
    else:
        item_exporter = ConsoleItemExporter()

    return item_exporter