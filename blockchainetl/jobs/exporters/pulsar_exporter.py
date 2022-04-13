import collections
import json
import logging
import pulsar

from blockchainetl.jobs.exporters.converters.composite_item_converter import CompositeItemConverter


class PulsarItemExporter:

    def __init__(self, output, token, item_type_to_topic_mapping, converters=()):
        self.item_type_to_topic_mapping = item_type_to_topic_mapping
        self.converter = CompositeItemConverter(converters)
        self.connection_url = self.get_connection_url(output)
        self.token = self.get_connection_token(token)
        self.client = pulsar.Client(self.connection_url, authentication=pulsar.AuthenticationToken(self.token))
        self.producer_map = {}

        for item_type in self.item_type_to_topic_mapping:
            self.producer_map[item_type] = self.client.create_producer(topic=item_type_to_topic_mapping[item_type])

    def get_connection_url(self, output):
        try:
            return output
        except KeyError:
            raise Exception('Invalid pulsar output param, It should be in format of "pulsar://localhost:6650"')

    def get_connection_token(self, output):
        try:
            return output
        except KeyError:
            raise Exception('Invalid pulsar token, It should be in format of "eyabcde..."')

    def open(self):
        pass

    def export_items(self, items):
        for item in items:
            self.export_item(item)

    def export_item(self, item):
        item_type = item.get('type')
        if item_type is not None and item_type in self.item_type_to_topic_mapping:
            data = json.dumps(item).encode('utf-8')
            return self.producer_map[item_type].send(data)
        else:
            logging.warning('Topic for item type "{}" is not configured.'.format(item_type))

    def convert_items(self, items):
        for item in items:
            yield self.converter.convert_item(item)

    def close(self):
        pass


def group_by_item_type(items):
    result = collections.defaultdict(list)
    for item in items:
        result[item.get('type')].append(item)

    return result
