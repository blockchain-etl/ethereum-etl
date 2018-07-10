from ethereumetl.exporters import CsvItemExporter
from ethereumetl.file_utils import get_file_handle, close_silently


class CompositeItemExporter:
    def __init__(self, filename_mapping, field_mapping):
        self.filename_mapping = filename_mapping
        self.field_mapping = field_mapping

        self.file_mapping = {}
        self.exporter_mapping = {}

    def open(self):
        for item_type, filename in self.filename_mapping.items():
            self.file_mapping[item_type] = get_file_handle(filename, binary=True)
            self.exporter_mapping[item_type] = CsvItemExporter(self.file_mapping[item_type],
                                                               fields_to_export=self.field_mapping[item_type])

    def export_item(self, item):
        item_type = item.get('type', None)
        if item_type is None:
            raise ValueError('type key is not found in item {}'.format(repr(item)))

        exporter = self.exporter_mapping[item_type]
        if exporter is None:
            raise ValueError('Exporter for item type {} not found'.format(item_type))
        exporter.export_item(item)

    def close(self):
        for file in self.file_mapping.values():
            close_silently(file)
