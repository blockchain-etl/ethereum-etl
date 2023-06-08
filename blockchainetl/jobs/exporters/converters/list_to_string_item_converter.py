import json

from blockchainetl.jobs.exporters.converters.simple_item_converter import SimpleItemConverter


class ListToStringItemConverter(SimpleItemConverter):

    def __init__(self, *keys):
        self.keys = set(keys) if keys else set()

    def convert_field(self, key, value):
        if key in self.keys and isinstance(value, list):
            return json.dumps(value)
        else:
            return value
