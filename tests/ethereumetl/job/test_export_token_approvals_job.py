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
from ethereumetl.web3_utils import build_web3

import tests.resources
from ethereumetl.jobs.export_token_approvals_job import ExportTokenApprovalsJob
from ethereumetl.jobs.exporters.token_approvals_item_exporter import token_approvals_item_exporter
from ethereumetl.thread_local_proxy import ThreadLocalProxy
from tests.ethereumetl.job.helpers import get_web3_provider
from tests.helpers import compare_lines_ignore_order, read_file

RESOURCE_GROUP = 'test_export_token_approvals_job'


def read_resource(resource_group, file_name):
    return tests.resources.read_resource([RESOURCE_GROUP, resource_group], file_name)


@pytest.mark.parametrize("start_block,end_block,batch_size,resource_group,web3_provider_type", [
    (483920, 483920, 1, 'block_with_approvals', 'mock')
])
def test_export_token_approvals_job(tmpdir, start_block, end_block, batch_size, resource_group, web3_provider_type):
    output_file = str(tmpdir.join('token_approvals.csv'))

    job = ExportTokenApprovalsJob(
        start_block=start_block, end_block=end_block, batch_size=batch_size,
        web3=ThreadLocalProxy(
            lambda: build_web3(get_web3_provider(web3_provider_type, lambda file: read_resource(resource_group, file)))
        ),
        item_exporter=token_approvals_item_exporter(output_file),
        max_workers=5
    )
    job.run()

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_token_approvals.csv'), read_file(output_file)
    )
