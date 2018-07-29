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

from ethereumetl.utils import hex_to_dec


class MockBatchWeb3Provider(object):
    def __init__(self, read_resource):
        self.read_resource = read_resource

    def make_request(self, text):
        batch = json.loads(text)
        ipc_response = []
        for req in batch:
            if req['method'] == 'eth_getBlockByNumber':
                block_number = hex_to_dec(req['params'][0])
                file_name = 'ipc_response.block.' + str(block_number) + '.json'
            elif req['method'] == 'eth_getCode':
                contract_address = req['params'][0]
                file_name = 'ipc_response.code.' + str(contract_address) + '.json'
            else:
                tx_hash = req['params'][0]
                file_name = 'ipc_response.receipt.' + str(tx_hash) + '.json'
            file_content = self.read_resource(file_name)
            ipc_response.append(json.loads(file_content))
        return ipc_response