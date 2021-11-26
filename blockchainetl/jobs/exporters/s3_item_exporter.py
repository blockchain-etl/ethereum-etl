import collections
import os, sys
import logging
import boto3
from blockchainetl.jobs.exporters.composite_item_exporter import CompositeItemExporter
from blockchainetl.jobs.exporters.converters.composite_item_converter import CompositeItemConverter
from blockchainetl.file_utils import get_file_handle, close_silently
from datetime import datetime
import csv
import json

from uuid import uuid4

class S3ItemExporter(CompositeItemExporter):

    def __init__(self, filename_mapping=None, bucket=None, converters=(), environment='dev', chain='ethereum'):
        self.filename_mapping = {
                'block': 'blocks.csv',
                'transaction': 'transactions.csv',
                'log': 'logs.json',
                'token_transfer': 'token_transfers.csv',
                'trace': 'traces.csv',
                'contract': 'contracts.csv',
                'token': 'tokens.csv'
                }
        self.field_mapping = {}
        self.file_mapping = {}
        self.exporter_mapping = {}
        self.counter_mapping = {}
        self.bucket = bucket
        self.converter = CompositeItemConverter(converters)
        self.logger = logging.getLogger('S3ItemExporter')
        self.s3 = boto3.client('s3')
        self.ENVIRONMENT = environment
        self.CHAIN = chain


    def upload(self, location, filename, type, block_date, item_id):
            self.s3.upload_file(filename, location, "data/{}/{}/{}/block_date={}/{}".format(self.ENVIRONMENT, self.CHAIN, filename.split('.')[0], block_date, item_id))

    def export_items(self, items):
        for item in items:
            self.export_item(item)
        self.upload_to_s3()

    def convert_items(self, items):
        for item in items:
            yield self.converter.convert_item(item)

    def extract_date_from_file(self, file):
        with open(file, 'r') as f:
            rows = []
            if file.endswith('csv'):
                csv.field_size_limit(sys.maxsize)
                reader = csv.DictReader(f, delimiter=",")
                next(reader)
                for row in reader:
                    rows.append(row.get('item_timestamp'))
            elif file.endswith('json'):
                for i in f:
                    data = json.loads(i)
                    rows.append(data.get('item_timestamp'))

            minimus = min(rows, key=lambda x: datetime.strptime(x.split('T')[0], '%Y-%m-%d'))
            return minimus.split('T')[0]

    def close(self):
        self.upload_to_s3()
        for item_type, file in self.file_mapping.items():
            close_silently(file)

    def flush(self, file):
        os.remove(file.name)
        from pathlib import Path
        Path(file.name).touch()
        return True

    def upload_to_s3(self):
        for item_type, file in self.file_mapping.items():
            counter = self.counter_mapping[item_type]
            if counter is not None and (counter.increment() - 1) > 0 and (os.stat(file.name).st_size > 0):
                self.logger.info('{} items exported: {}'.format(item_type, counter.increment() - 1))
                self.upload(self.bucket, file.name, item_type, self.extract_date_from_file(file.name), str(uuid4()) + '_' + file.name)
                self.logger.info('Uploaded {} to S3'.format(item_type))
                self.flush(file)
                self.logger.info('Flushed {} file'.format(item_type))
        self.open()
