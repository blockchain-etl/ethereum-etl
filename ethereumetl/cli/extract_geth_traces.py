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
import csv
import json

import click

from blockchainetl.file_utils import smart_open
from ethereumetl.jobs.exporters.traces_item_exporter import traces_item_exporter
from ethereumetl.jobs.extract_geth_traces_job import ExtractGethTracesJob
from blockchainetl.logging_utils import logging_basic_config

logging_basic_config()


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-i', '--input', required=True, type=str, help='The JSON file containing geth traces.')
@click.option('-b', '--batch-size', default=100, show_default=True, type=int, help='The number of blocks to filter at a time.')
@click.option('-o', '--output', default='-', show_default=True, type=str, help='The output file. If not specified stdout is used.')
@click.option('-w', '--max-workers', default=5, show_default=True, type=int, help='The maximum number of workers.')
def extract_geth_traces(input, batch_size, output, max_workers):
    """Extracts geth traces from JSON lines file."""
    with smart_open(input, 'r') as geth_traces_file:
        if input.endswith('.json'):
            traces_iterable = (json.loads(line) for line in geth_traces_file)
        else:
            traces_iterable = (trace for trace in csv.DictReader(geth_traces_file))
        job = ExtractGethTracesJob(
            traces_iterable=traces_iterable,
            batch_size=batch_size,
            max_workers=max_workers,
            item_exporter=traces_item_exporter(output))

        job.run()
