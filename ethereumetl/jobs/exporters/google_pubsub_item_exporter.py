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

import json
import logging

from google.cloud import pubsub_v1


class GooglePubSubItemExporter:

    def __init__(self, item_type_to_topic_mapping, timeout=300):
        self.item_type_to_topic_mapping = item_type_to_topic_mapping

        batch_settings = pubsub_v1.types.BatchSettings(
            max_bytes=1024 * 5,  # 5 kilobytes
            max_latency=1,  # 1 second
            max_messages=1000,
        )

        self.publisher = pubsub_v1.PublisherClient(batch_settings)
        self.timeout = timeout

    def open(self):
        pass

    def export_items(self, items):
        futures = []
        for item in items:
            message_future = self.export_item(item)
            futures.append(message_future)

        for future in futures:
            # result() blocks until the message is published.
            future.result(timeout=self.timeout)

    def export_item(self, item):
        item_type = item.get('type')
        if item_type is not None and item_type in self.item_type_to_topic_mapping:
            topic_path = self.item_type_to_topic_mapping.get(item_type)
            data = json.dumps(item).encode('utf-8')
            message_future = self.publisher.publish(topic_path, data=data)
            return message_future
        else:
            logging.warning('Topic for item type "{}" is not configured.'.format(item_type))

    def close(self):
        pass
