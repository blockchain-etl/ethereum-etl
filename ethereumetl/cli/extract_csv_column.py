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

from ethereumetl.csv_utils import set_max_field_size_limit
from blockchainetl.file_utils import smart_open


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-i', '--input', default='-', show_default=True, type=str, help='The input file. If not specified stdin is used.')
@click.option('-o', '--output', default='-', show_default=True, type=str, help='The output file. If not specified stdout is used.')
@click.option('-c', '--column', required=True, type=str, help='The csv column name to extract.')
def extract_csv_column(input, output, column):
    """Extracts column from given CSV file. Deprecated - use extract_field."""
    set_max_field_size_limit()

    with smart_open(input, 'r') as input_file, smart_open(output, 'w') as output_file:
        reader = csv.DictReader(input_file)
        for row in reader:
            output_file.write(row[column] + '\n')
