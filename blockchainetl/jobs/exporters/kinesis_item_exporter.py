# MIT License
#
# Copyright (c) 2022 CoinStats LLC
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
import typing as t
import uuid
from itertools import zip_longest

import boto3

_KINESIS_BATCH_LIMIT = 500


def _uuid_partition_key(_: dict) -> str:
    return uuid.uuid4().hex


class KinesisItemExporter:
    def __init__(
            self,
            stream_name: str,
            partition_key_callable: t.Callable[[dict], str] = _uuid_partition_key,
    ):
        import boto3
        self._stream_name = stream_name
        self._partition_key_callable = partition_key_callable
        self._kinesis_client = None  # initialized in .open

    def open(self) -> None:
        self._kinesis_client = boto3.client('kinesis')

    def export_items(self, items: t.Iterable[dict]) -> None:
        sentinel = object()
        chunks = zip_longest(
            *(iter(items),) * _KINESIS_BATCH_LIMIT,
            fillvalue=sentinel,
        )
        for chunk in chunks:
            self._kinesis_client.put_records(
                StreamName=self._stream_name,
                Records=[
                    {
                        'Data': _serialize_item(item),
                        'PartitionKey': self._partition_key_callable(item),
                    }
                    for item in chunk
                    if item is not sentinel
                ],
            )

    def export_item(self, item: dict) -> None:
        self._kinesis_client.put_record(
            StreamName=self._stream_name,
            Data=_serialize_item(item),
            PartitionKey=self._partition_key_callable(item),
        )

    def close(self):
        pass


def _serialize_item(item: dict) -> bytes:
    return json.dumps(item).encode()
