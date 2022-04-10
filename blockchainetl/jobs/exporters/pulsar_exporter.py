import collections
import json
import logging
import pulsar

from blockchainetl.jobs.exporters.converters.composite_item_converter import CompositeItemConverter


class PulsarItemExporter:

    def __init__(self, output, item_type_to_topic_mapping, converters=()):
        self.item_type_to_topic_mapping = item_type_to_topic_mapping
        self.converter = CompositeItemConverter(converters)
        self.connection_url = self.get_connection_url(output)
        self.client = pulsar.Client(self.connection_url,
                                    authentication=pulsar.AuthenticationToken(
                                        'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2NDkzOTA5OTYsImlzcyI6ImRhdGFzdGF4Iiwic3ViIjoiY2xpZW50OzY1ZmM3ZDExLTZmZDItNDIzOC1hMjU4LWQ4OTNiMDBhYjIzMDtaWFJvTFdWMGJBPT07N2MwYWE5ZDI4OSIsInRva2VuaWQiOiI3YzBhYTlkMjg5In0.J26P7qSdm3do5jTS_4B45RPcdKW0Xx0V3sWDwYOcMF2828O0uyetSllXg0iMl3hOhiKulSjz4ifG0aeUywBwTxeV0wjbn0zCF4HVyHhFL1-ci-DHeEGisD1yRA6MU3fjtHZQqznSYmYfA049-SDyX0H5afIzxit1B5PSuHrUeY4PmAJKM2OkqyBpYpN476Oa64YQoLRt75QGUrcZzphqbbMhMmAxDp1dL-vMe36BKKIkPT7v7AnhGKjooMxraZ4R1S9LLEKCHhrs13KKriNTeMKfTHyD3KS-c2s_TepwneVFuwD4VtCNfJjLL-efJbDYzr8ISv81ye3dOmey55IFBg'),
                                    )

    def get_connection_url(self, output):
        try:
            print(output)
            return output
        except KeyError:
            raise Exception('Invalid pulsar output param, It should be in format of "pulsar://localhost:6650"')

    def open(self):
        pass

    def export_items(self, items):
        for item in items:
            self.export_item(item)

    def export_item(self, item):
        item_type = item.get('type')
        if item_type is not None and item_type in self.item_type_to_topic_mapping:
            producer_endpoint = 'persistent://eth-etl/default/' + self.item_type_to_topic_mapping[item_type]
            data = json.dumps(item).encode('utf-8')
            producer = self.client.create_producer(
                topic=producer_endpoint
            )
            return producer.send(data)
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
