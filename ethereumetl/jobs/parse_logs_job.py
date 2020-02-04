#  MIT License
#
#  Copyright (c) 2020 Evgeny Medvedev, evge.medvedev@gmail.com
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

from web3.utils.events import (
    get_event_data,
)

log_entry = {
    'topics': ['0x1f9c649fe47e58bb60f4e52f0d90e4c47a526c9f90c5113df842c025970b66ad',
               '0xd8321837f963bcc931d1ac71557689dcf6b35ea541a11bad4907ac76f0525d37',
               '0xd8321837f963bcc931d1ac71557689dcf6b35ea541a11bad4907ac76f0525d37'],
    'data': '0x000000000000000000000000000000000000000000000000002386f26fc10000000000000000000000000000000000000000000000000000000000005a7c42f9',
    'name': None,
    'logIndex': None,
    'transactionIndex': None,
    'transactionHash': None,
    'address': None,
    'blockHash': None,
    'blockNumber': None,

}

# Convert hex strings to bytes
log_entry['topics'] = [bytes.fromhex(topic.replace('0x', '')) for topic in log_entry['topics']]
log_entry['data'] = bytes.fromhex(log_entry['data'].replace('0x', ''))


event_abi = {
    "anonymous": False,
    "inputs": [
        {
            "indexed": True,
            "name": "hash",
            "type": "bytes32"
        },
        {
            "indexed": True,
            "name": "name",
            "type": "string"
        },
        {
            "indexed": False,
            "name": "value",
            "type": "uint256"
        },
        {
            "indexed": False,
            "name": "registrationDate",
            "type": "uint256"
        }
    ],
    "name": "HashInvalidated",
    "type": "event"
}

rich_log = get_event_data(event_abi, log_entry)

print(rich_log.args)
