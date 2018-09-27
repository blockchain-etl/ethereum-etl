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


import argparse
import json

from google.cloud import pubsub_v1

from ethereumetl.logging_utils import logging_basic_config

logging_basic_config()

parser = argparse.ArgumentParser(description='')

args = parser.parse_args()

publisher = pubsub_v1.PublisherClient()

item = {
    'type': 'token_transfer',
    'value': 10000010000000000000000,
    'from_address': '0x2a0c0dbecc7e4d658f48e01e3fa353f44050c208',
    'to_address': '0x0c73365016f72cc8d72feb2aeb16fb9eae7c8429',
    'token_address': '0xef68e7c694f40c8202821edf525de3782458639f',
}
data = json.dumps(item).encode('utf-8')
future = publisher.publish('projects/coinfi-dev/topics/large_transactions', data=data)
result = future.result()
print(result)