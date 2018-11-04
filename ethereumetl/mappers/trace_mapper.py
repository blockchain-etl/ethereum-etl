# MIT License
#
# Copyright (c) 2018 Evgeniy Filatov, evgeniyfilatov@gmail.com
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


from ethereumetl.domain.trace import EthTrace
from ethereumetl.utils import hex_to_dec, to_normalized_address


class EthTraceMapper(object):
    def json_dict_to_trace(self, json_dict):
        trace = EthTrace()

        trace.block_number = json_dict.get('blockNumber', None)
        trace.transaction_hash = json_dict.get('transactionHash', None)
        trace.transaction_index = json_dict.get('transactionPosition', None)
        trace.subtraces = json_dict.get('subtraces', None)
        trace.trace_address = json_dict.get('traceAddress', [])

        error = json_dict.get('error', None)

        if error:
            trace.error = error

        action = json_dict.get('action', None)
        if action is None:
            action = {}
        result = json_dict.get('result', None)
        if result is None:
            result = {}

        trace_type = json_dict.get('type', None)
        trace.trace_type = trace_type

        # common fields in call/create
        if trace_type in ('call', 'create'):
            trace.from_address = to_normalized_address(action.get('from', None))
            trace.value = hex_to_dec(action.get('value', None))
            trace.gas = hex_to_dec(action.get('gas', None))
            trace.gas_used = hex_to_dec(result.get('gasUsed', None))

        # process different trace types
        if trace_type == 'call':
            trace.call_type = action.get('callType', None)
            trace.to_address = to_normalized_address(action.get('to', None))
            trace.input = action.get('input', None)
            trace.output = result.get('output', None)
        elif trace_type == 'create':
            trace.contract_address = result.get('address', None)
            trace.input = action.get('init', None)
            trace.output = result.get('code', None)
        elif trace_type == 'suicide':
            trace.from_address = to_normalized_address(action.get('address', None))
            trace.to_address = to_normalized_address(action.get('refundAddress', None))
            trace.value = hex_to_dec(action.get('balance', None))
        elif trace_type == 'reward':
            trace.to_address = to_normalized_address(action.get('author', None))
            trace.value = hex_to_dec(action.get('value', None))
            trace.reward_type = action.get('rewardType', None)

        return trace

    def geth_trace_to_traces(self, geth_trace):
        block_number = geth_trace.block_number
        transaction_traces = geth_trace.transaction_traces

        traces = []

        for tx_index, tx_trace in enumerate(transaction_traces):
            traces.extend(self._iterate_transaction_trace(
                block_number,
                tx_index,
                tx_trace,
            ))

        return traces

    def _iterate_transaction_trace(self, block_number, tx_index, tx_trace, trace_address=[]):
        trace = EthTrace()

        trace.block_number = block_number
        trace.transaction_index = tx_index

        trace.from_address = to_normalized_address(tx_trace.get('from', None))
        trace.to_address = to_normalized_address(tx_trace.get('to', None))

        trace.input = tx_trace.get('input', None)
        trace.output = tx_trace.get('output', None)

        trace.value = hex_to_dec(tx_trace.get('value', None))
        trace.gas = hex_to_dec(tx_trace.get('gas', None))
        trace.gas_used = hex_to_dec(tx_trace.get('gasUsed', None))

        trace.error = tx_trace.get('error', None)

        # lowercase for compatibility with parity traces
        trace.trace_type = tx_trace.get('type', None).lower()

        if trace.trace_type == 'selfdestruct':
            # rename to suicide for compatibility with parity traces
            trace.trace_type = 'suicide'
        elif trace.trace_type == 'create':
            # move created contract address from `to_address` to `contract_address`
            trace.to_address = None
            trace.contract_address = to_normalized_address(tx_trace.get('to', None))
        elif trace.trace_type in ('call', 'callcode', 'delegatecall', 'staticcall'):
            trace.call_type = trace.trace_type
            trace.trace_type = 'call'

        result = [trace]

        calls = tx_trace.get('calls', [])

        trace.subtraces = len(calls)
        trace.trace_address = trace_address

        for call_index, call_trace in enumerate(calls):
            result.extend(self._iterate_transaction_trace(
                block_number,
                tx_index,
                call_trace,
                trace_address + [call_index]
            ))

        return result

    def trace_to_dict(self, trace):
        return {
            'type': 'trace',
            'block_number': trace.block_number,
            'transaction_hash': trace.transaction_hash,
            'transaction_index': trace.transaction_index,
            'from_address': trace.from_address,
            'to_address': trace.to_address,
            'value': trace.value,
            'contract_address': trace.contract_address,
            'input': trace.input,
            'output': trace.output,
            'trace_type': trace.trace_type,
            'call_type': trace.call_type,
            'reward_type': trace.reward_type,
            'gas': trace.gas,
            'gas_used': trace.gas_used,
            'subtraces': trace.subtraces,
            'trace_address': trace.trace_address,
            'error': trace.error,
        }
