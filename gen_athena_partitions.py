import argparse

parser = argparse.ArgumentParser(
    description='Generates ALTER TABLE SQL statement for adding partitions for a table.')
parser.add_argument('--table', default='blocks', type=str, help='Table name')
parser.add_argument('--s3-path', default='s3://<your_bucket>/athena/lab1/blocks/', type=str, help='S3 bucket name')
parser.add_argument('--start-block', default=0, type=int, help='Start block')
parser.add_argument('--end-block', required=True, type=int, help='End block')
parser.add_argument('--batch-size', default=100000, type=int, help='The number of blocks to filter at a time.')

args = parser.parse_args()

statement = "ALTER TABLE {} ADD IF NOT EXISTS\n".format(args.table)


def pad_zeros(num):
    return '{:08d}'.format(num)


for batch_start_block in range(args.start_block, args.end_block + 1, args.batch_size):
    batch_end_block = min(batch_start_block + args.batch_size - 1, args.end_block)
    file_name = "{}_{}_{}.csv".format(args.table, pad_zeros(batch_start_block), pad_zeros(batch_end_block))
    statement += "PARTITION(start_block={}, end_block={}) LOCATION '{}{}'\n" \
        .format(batch_start_block, batch_end_block, args.s3_path, file_name)

statement += ';\n'
statement += 'MSCK REPAIR TABLE {};\n'.format(args.table)

print(statement)
