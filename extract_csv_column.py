import argparse
import csv

from ethereumetl.csv_utils import set_max_field_size_limit
from ethereumetl.utils import smart_open

parser = argparse.ArgumentParser(description='Extracts a single column from a given csv file.')
parser.add_argument('--input', default=None, type=str, help='The input file. If not specified stdin is used.')
parser.add_argument('--output', default=None, type=str, help='The output file. If not specified stdout is used.')
parser.add_argument('--column', required=True, type=str, help='The csv column name to extract.')

args = parser.parse_args()

set_max_field_size_limit()

with smart_open(args.input, 'r') as input_file, smart_open(args.output, 'w') as output_file:
    reader = csv.DictReader(input_file)  # read rows into a dictionary format
    for row in reader:
        output_file.write(row[args.column] + '\n')

