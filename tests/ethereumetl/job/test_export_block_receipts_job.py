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


import pytest

import tests.resources
from ethereumetl.jobs.export_block_receipts_job import ExportBlockReceiptsJob
from ethereumetl.jobs.exporters.receipts_and_logs_item_exporter import receipts_and_logs_item_exporter
from ethereumetl.thread_local_proxy import ThreadLocalProxy
from tests.ethereumetl.job.helpers import get_web3_provider
from tests.helpers import compare_lines_ignore_order, read_file, skip_if_slow_tests_disabled

RESOURCE_GROUP = 'test_export_block_receipts_job'


def read_resource(resource_group, file_name):
    return tests.resources.read_resource([RESOURCE_GROUP, resource_group], file_name)


DEFAULT_BLOCK_NUMBER = int("0x76250", 16)


@pytest.mark.parametrize("batch_size,block_number,output_format,resource_group,web3_provider_type", [
    (1, DEFAULT_BLOCK_NUMBER, 'csv', 'receipts_with_logs', 'mock'),
    (2, DEFAULT_BLOCK_NUMBER, 'csv', 'receipts_with_logs', 'mock'),
    (2, DEFAULT_BLOCK_NUMBER, 'json', 'receipts_with_logs', 'mock'),
    skip_if_slow_tests_disabled((1, DEFAULT_BLOCK_NUMBER, 'csv', 'receipts_with_logs', 'infura')),
    skip_if_slow_tests_disabled((2, DEFAULT_BLOCK_NUMBER, 'json', 'receipts_with_logs', 'infura'))
])
def test_export_receipts_job(tmpdir, batch_size, block_number, output_format, resource_group, web3_provider_type):
    receipts_output_file = str(tmpdir.join('actual_receipts.' + output_format))
    logs_output_file = str(tmpdir.join('actual_logs.' + output_format))

    job = ExportBlockReceiptsJob(
        start_block=block_number,
        end_block=block_number,
        batch_size=batch_size,
        batch_web3_provider=ThreadLocalProxy(
            lambda: get_web3_provider(web3_provider_type, lambda file: read_resource(resource_group, file), batch=True)
        ),
        max_workers=5,
        item_exporter=receipts_and_logs_item_exporter(receipts_output_file, logs_output_file),
        export_receipts=receipts_output_file is not None,
        export_logs=logs_output_file is not None
    )
    job.run()

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_receipts.' + output_format), read_file(receipts_output_file)
    )

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_logs.' + output_format), read_file(logs_output_file)
    )
