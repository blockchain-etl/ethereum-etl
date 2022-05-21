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
from confluent_kafka import Producer
from timeout_decorator import timeout_decorator

import logging

import socket
import json


class KafkaItemExporter:
    def __init__(self, item_type_to_topic_mapping) -> None:
        logging.basicConfig(
            level=logging.INFO,
            # filename="/data/mempool/mempool.log",
            filename="msessage-publish.log",
            format='{"time" : "%(asctime)s", "level" : "%(levelname)s" , "message" : "%(message)s"}',
        )

        conf = {
            "bootstrap.servers": "104.197.163.1:9092",
            "client.id": socket.gethostname(),
        }
        producer = Producer(conf)
        self.item_type_to_topic_mapping = item_type_to_topic_mapping
        self.producer = producer
        self.logging = logging.getLogger(__name__)
        # self.topic = topic

    def open(self):
        pass

    @timeout_decorator.timeout(300)
    def _export_items_with_timeout(self, items):
        futures = []
        for item in items:
            message_future = self.export_item(item)
            futures.append(message_future)

        for future in futures:
            # result() blocks until the message is published.
            future.result()

    def export_item(self, item):
        item_type = item.get("type")
        has_item_type = item_type is not None
        if has_item_type and item_type in self.item_type_to_topic_mapping:
            data = json.dumps(item).encode("utf-8")
            message_future = self.write_txns(data)
            return message_future
        else:
            logging.warning('Topic for item type "{}" is not configured.')

    def get_message_attributes(self, item):
        attributes = {}

        for attr_name in self.message_attributes:
            if item.get(attr_name) is not None:
                attributes[attr_name] = item.get(attr_name)

        return attributes

    def close(self):
        pass

    def write_txns(self, enriched_data: str):
        def acked(err, msg):
            if err is not None:
                self.logging.error(
                    "Failed to deliver message: %s: %s" % (str(msg), str(err))
                )
            else:
                self.logging.info("Message produced: %s" % msg)

        self.producer.produce(self.topic, key="", value=enriched_data, callback=acked)
        self.producer.poll(1)
