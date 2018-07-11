import argparse
import csv

from ethereumetl.csv_utils import set_max_field_size_limit
from ethereumetl.file_utils import smart_open

parser = argparse.ArgumentParser(description='Extracts a single column from a given csv file.')
parser.add_argument('-i', '--input', default=None, type=str, help='The input file. If not specified stdin is used.')
parser.add_argument('-o', '--output', default=None, type=str, help='The output file. If not specified stdout is used.')
parser.add_argument('-c', '--column', required=True, type=str, help='The csv column name to extract.')
parser.add_argument('-c', '--transformer-type', required=True, type=str,
                    choices=['clean_ascii', 'max'], help='The transformer type.')
parser.add_argument('-c', '--transformer-args', default=None, type=str, nargs='+',
                    help='Transformer arguments.')

args = parser.parse_args()

set_max_field_size_limit()


def parse_transformer(transformer_type, transformer_args):
    if transformer_type == 'clean_ascii':
        return clean_ascii_transformer
    elif transformer_type == 'max':
        if len(transformer_args) == 0:
            raise ValueError('You must provide maximum value for maximum transformer')
        maximum = int(transformer_args[0])
        if len(transformer_args) > 1:
            replacement = int(transformer_args[1])
        else:
            replacement = None

        def transformer(val):
            return max_transformer(val, maximum, replacement)

        return transformer
    else:
        raise ValueError('transformer is not recognized {}'.format(transformer_type))


ASCII_0 = 0


def clean_ascii_transformer(val):
    return val.translate({ASCII_0: None})


def max_transformer(val, maximum, replacement):
    return val if val <= maximum else replacement


def process_file():
    with smart_open(args.input, 'r') as input_file, smart_open(args.output, 'w') as output_file:
        reader = csv.DictReader(input_file)
        writer = csv.DictWriter(output_file, reader.fieldnames)
        writer.writeheader()
        transformer = parse_transformer(args.transformer_type, args.transformer_args)
        for row in reader:
            value = row[args.column]
            transformed_value = transformer(value)
            row[args.column] = transformed_value
            writer.writerow(row)


process_file()
