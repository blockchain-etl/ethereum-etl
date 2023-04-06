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
from ethereumetl.jobs.export_blocks_job import ExportBlocksJob
from ethereumetl.jobs.exporters.blocks_and_transactions_item_exporter import blocks_and_transactions_item_exporter
from ethereumetl.thread_local_proxy import ThreadLocalProxy
from tests.ethereumetl.job.helpers import get_web3_provider
from tests.helpers import compare_lines_ignore_order, read_file, skip_if_slow_tests_disabled

RESOURCE_GROUP = 'test_export_blocks_job'


def read_resource(resource_group, file_name):
    return tests.resources.read_resource([RESOURCE_GROUP, resource_group], file_name)


@pytest.mark.parametrize("start_block,end_block,batch_size,resource_group,web3_provider_type", [
    (0, 0, 1, 'block_without_transactions', 'mock'),
    (483920, 483920, 1, 'block_with_logs', 'mock'),
    (47218, 47219, 1, 'blocks_with_transactions', 'mock'),
    (47218, 47219, 2, 'blocks_with_transactions', 'mock'),
    skip_if_slow_tests_disabled((0, 0, 1, 'block_without_transactions', 'infura')),
    skip_if_slow_tests_disabled((483920, 483920, 1, 'block_with_logs', 'infura')),
    skip_if_slow_tests_disabled((47218, 47219, 2, 'blocks_with_transactions', 'infura')),
])
def test_export_blocks_job(tmpdir, start_block, end_block, batch_size, resource_group, web3_provider_type):
    blocks_output_file = str(tmpdir.join('actual_blocks.csv'))
    transactions_output_file = str(tmpdir.join('actual_transactions.csv'))

    job = ExportBlocksJob(
        start_block=start_block, end_block=end_block, batch_size=batch_size,
        batch_web3_provider=ThreadLocalProxy(
            lambda: get_web3_provider(web3_provider_type, lambda file: read_resource(resource_group, file), batch=True)
        ),
        max_workers=5,
        item_exporter=blocks_and_transactions_item_exporter(blocks_output_file, transactions_output_file),
        export_blocks=blocks_output_file is not None,
        export_transactions=transactions_output_file is not None
    )
    job.run()

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_blocks.csv'), read_file(blocks_output_file)
    )

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_transactions.csv'), read_file(transactions_output_file)
    )
