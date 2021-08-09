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


import click
import csv
import json

from blockchainetl.file_utils import smart_open
from blockchainetl.jobs.exporters.converters.int_to_string_item_converter import IntToStringItemConverter
from ethereumetl.jobs.exporters.token_transfers_item_exporter import token_transfers_item_exporter
from ethereumetl.jobs.extract_token_transfers_job import ExtractTokenTransfersJob
from blockchainetl.logging_utils import logging_basic_config

logging_basic_config()


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-l', '--logs', type=str, required=True, help='The CSV file containing receipt logs.')
@click.option('-b', '--batch-size', default=100, show_default=True, type=int, help='The number of blocks to filter at a time.')
@click.option('-o', '--output', default='-', show_default=True, type=str, help='The output file. If not specified stdout is used.')
@click.option('-w', '--max-workers', default=5, show_default=True, type=int, help='The maximum number of workers.')
@click.option('--values-as-strings', default=False, show_default=True, is_flag=True, help='Whether to convert values to strings.')
def extract_token_transfers(logs, batch_size, output, max_workers, values_as_strings=False):
    """Extracts ERC20/ERC721 transfers from logs file."""
    with smart_open(logs, 'r') as logs_file:
        if logs.endswith('.json'):
            logs_reader = (json.loads(line) for line in logs_file)
        else:
            logs_reader = csv.DictReader(logs_file)
        converters = [IntToStringItemConverter(keys=['value'])] if values_as_strings else []
        job = ExtractTokenTransfersJob(
            logs_iterable=logs_reader,
            batch_size=batch_size,
            max_workers=max_workers,
            item_exporter=token_transfers_item_exporter(output, converters=converters))

        job.run()
