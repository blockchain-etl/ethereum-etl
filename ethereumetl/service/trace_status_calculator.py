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

from collections import defaultdict


def calculate_trace_statuses(traces):
    # set default values
    for trace in traces:
        if trace.error is not None and len(trace.error) > 0:
            trace.status = 0
        else:
            trace.status = 1

    # group by transaction
    grouped_transaction_traces = defaultdict(list)
    for trace in traces:
        if trace.transaction_hash is not None and len(trace.transaction_hash) > 0:
            grouped_transaction_traces[trace.transaction_hash].append(trace)

    # calculate statuses for each transaction
    for transaction_traces in grouped_transaction_traces.values():
        calculate_trace_statuses_for_single_transaction(transaction_traces)

    return traces


def calculate_trace_statuses_for_single_transaction(all_traces):
    """O(n * log(n))"""
    sorted_traces = sorted(all_traces, key=lambda trace: len(trace.trace_address or []))
    indexed_traces = {trace_address_to_str(trace.trace_address): trace for trace in sorted_traces}

    # if a parent trace failed the child trace set failed also. Because of the sorting order all parent trace statuses
    # are calculated before child trace statuses.
    for trace in sorted_traces:
        if len(trace.trace_address) > 0:
            parent_trace = indexed_traces.get(trace_address_to_str(trace.trace_address[:-1]))
            if parent_trace is None:
                raise ValueError('A parent trace for trace with trace_address {} in transaction {} is not found'
                                 .format(trace.trace_address, trace.transaction_hash))
            if parent_trace.status == 0:
                trace.status = 0


def trace_address_to_str(trace_address):
    if trace_address is None or len(trace_address) == 0:
        return ''

    return ','.join([str(address_point) for address_point in trace_address])
