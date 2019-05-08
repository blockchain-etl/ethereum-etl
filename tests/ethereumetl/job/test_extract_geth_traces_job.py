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

import json

import pytest

import tests.resources
from ethereumetl.jobs.exporters.traces_item_exporter import traces_item_exporter
from ethereumetl.jobs.extract_geth_traces_job import ExtractGethTracesJob
from tests.helpers import compare_lines_ignore_order, read_file

RESOURCE_GROUP = 'test_extract_geth_traces_job'


def read_resource(resource_group, file_name):
    return tests.resources.read_resource([RESOURCE_GROUP, resource_group], file_name)


@pytest.mark.parametrize('resource_group', [
    'block_without_transactions',
    'block_with_create',
    'block_with_suicide',
    'block_with_subtraces',
    'block_with_error',
])
def test_extract_traces_job(tmpdir, resource_group):
    output_file = str(tmpdir.join('actual_traces.csv'))

    geth_traces_content = read_resource(resource_group, 'geth_traces.json')
    traces_iterable = (json.loads(line) for line in geth_traces_content.splitlines())
    job = ExtractGethTracesJob(
        traces_iterable=traces_iterable,
        batch_size=2,
        item_exporter=traces_item_exporter(output_file),
        max_workers=5
    )
    job.run()

    print('=====================')
    print(read_file(output_file))
    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_traces.csv'), read_file(output_file)
    )
