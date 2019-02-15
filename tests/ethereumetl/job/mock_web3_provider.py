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

from web3 import IPCProvider


class MockWeb3Provider(IPCProvider):
    def __init__(self, read_resource):
        self.read_resource = read_resource

    def make_request(self, method, params):
        if method == 'eth_call':
            to = params[0]['to'].lower()
            data = params[0]['data']
            file_name = '{}_{}_{}.json'.format(method, to, data)
        # TODO: Remove this when this issue is fixed
        # https://github.com/paritytech/parity-ethereum/issues/9822
        elif method == 'trace_block':
            file_name = 'trace_filter.json'
        else:
            file_name = method + '.json'
        file_content = self.read_resource(file_name)
        return json.loads(file_content)
