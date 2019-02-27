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


from ethereumetl.mappers.trace_mapper import EthTraceMapper


class EthSpecialTraceService(object):

    def __init__(self):
        self.trace_mapper = EthTraceMapper()

    def get_genesis_traces(self):
        from ethereumetl.mainnet_genesis_alloc import MAINNET_GENESIS_ALLOC
        genesis_traces = [self.trace_mapper.genesis_alloc_to_trace(alloc)
                          for alloc in MAINNET_GENESIS_ALLOC]
        return genesis_traces

    def get_daofork_traces(self):
        from ethereumetl.mainnet_daofork_state_changes import MAINNET_DAOFORK_STATE_CHANGES
        daofork_traces = [self.trace_mapper.daofork_state_change_to_trace(change)
                          for change in MAINNET_DAOFORK_STATE_CHANGES]
        return daofork_traces
