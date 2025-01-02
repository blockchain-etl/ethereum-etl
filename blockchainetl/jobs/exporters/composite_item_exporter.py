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
from blockchainetl.jobs.exporters.converters.composite_item_converter import CompositeItemConverter



class CompositeItemExporter:
    def __init__(self, filename_mapping=None, field_mapping=None, item_exporters=None):
        self.filename_mapping = filename_mapping or {}
        self.field_mapping = field_mapping or {}
        self.exporter_mapping = {}
        self.file_mapping = {}
        
        # If item_exporters is provided, use them directly
        if item_exporters:
            self.exporter_mapping = item_exporters
        
    def open(self):
        # If we have direct exporters, just open them
        if self.exporter_mapping:
            for exporter in self.exporter_mapping.values():
                exporter.open()
            return

        # Otherwise, create file-based exporters
        for item_type, filename in self.filename_mapping.items():
            self.file_mapping[item_type] = get_file_handle(filename)
            self.exporter_mapping[item_type] = CsvItemExporter(
                self.file_mapping[item_type],
                fields_to_export=self.field_mapping.get(item_type),
                include_headers_line=True
            )
            self.exporter_mapping[item_type].start_exporting()

    def export_item(self, item):
        item_type = item.get('type')
        if item_type is None:
            raise ValueError(f'type key is not found in item {item}')

        exporter = self.exporter_mapping.get(item_type)
        if exporter is None:
            raise ValueError(f'Exporter for item type {item_type} not found')
            
        exporter.export_item(item)

    def close(self):
        for exporter in self.exporter_mapping.values():
            exporter.finish_exporting()
        for file in self.file_mapping.values():
            close_silently(file)
