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
import logging

from blockchainetl.atomic_counter import AtomicCounter
from blockchainetl.exporters import CsvItemExporter, JsonLinesItemExporter
from blockchainetl.file_utils import get_file_handle, close_silently


class CompositeItemExporter:
    def __init__(self, filename_mapping, field_mapping=None):
        self.filename_mapping = filename_mapping
        self.field_mapping = field_mapping or {}

        self.file_mapping = {}
        self.exporter_mapping = {}
        self.counter_mapping = {}

        self.logger = logging.getLogger('CompositeItemExporter')

    def open(self):
        for item_type, filename in self.filename_mapping.items():
            file = get_file_handle(filename, binary=True)
            fields = self.field_mapping.get(item_type)
            self.file_mapping[item_type] = file
            if str(filename).endswith('.json'):
                item_exporter = JsonLinesItemExporter(file, fields_to_export=fields)
            else:
                item_exporter = CsvItemExporter(file, fields_to_export=fields)
            self.exporter_mapping[item_type] = item_exporter

            self.counter_mapping[item_type] = AtomicCounter()

    def export_items(self, items):
        for item in items:
            self.export_item(item)

    def export_item(self, item):
        item_type = item.get('type')
        if item_type is None:
            raise ValueError('"type" key is not found in item {}'.format(repr(item)))

        exporter = self.exporter_mapping.get(item_type)
        if exporter is None:
            raise ValueError('Exporter for item type {} not found'.format(item_type))
        exporter.export_item(item)

        counter = self.counter_mapping.get(item_type)
        if counter is not None:
            counter.increment()

    def close(self):
        for item_type, file in self.file_mapping.items():
            close_silently(file)
            counter = self.counter_mapping[item_type]
            if counter is not None:
                self.logger.info('{} items exported: {}'.format(item_type, counter.increment() - 1))
