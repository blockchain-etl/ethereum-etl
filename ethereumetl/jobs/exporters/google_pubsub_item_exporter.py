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

from google.cloud import pubsub_v1


class GooglePubSubItemExporter:

    def __init__(self, topic_path):
        self.topic_path = topic_path

        batch_settings = pubsub_v1.types.BatchSettings(
            max_bytes=1024 * 5,  # 5 kilobytes
            max_latency=2,  # 2 seconds
        )

        self.publisher = pubsub_v1.PublisherClient(batch_settings)

    def open(self):
        pass

    def export_items(self, items):
        futures = []
        for item in items:
            message_future = self.export_item(item)
            futures.append(message_future)

        for future in futures:
            # result() blocks until the message is published.
            future.result()

    def export_item(self, item):
        data = json.dumps(item).encode('utf-8')
        message_future = self.publisher.publish(self.topic_path, data=data)
        return message_future

    def close(self):
        pass
