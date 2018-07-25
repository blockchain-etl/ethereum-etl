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

import csv
import io

import pytest

import tests.resources
from ethereumetl.jobs.exporters.erc20_transfers_item_exporter import erc20_transfers_item_exporter
from ethereumetl.jobs.extract_erc20_transfers_job import ExtractErc20TransfersJob
from tests.helpers import compare_lines_ignore_order, read_file

RESOURCE_GROUP = 'test_extract_erc20_transfers_job'


def read_resource(resource_group, file_name):
    return tests.resources.read_resource([RESOURCE_GROUP, resource_group], file_name)


@pytest.mark.parametrize('resource_group', [
    'logs'
])
def test_export_erc20_transfers_job(tmpdir, resource_group):
    output_file = tmpdir.join('erc20_transfers.csv')

    logs_content = read_resource(resource_group, 'logs.csv')
    logs_csv_reader = csv.DictReader(io.StringIO(logs_content))
    job = ExtractErc20TransfersJob(
        logs_iterable=logs_csv_reader,
        batch_size=2,
        item_exporter=erc20_transfers_item_exporter(output_file),
        max_workers=5
    )
    job.run()

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_erc20_transfers.csv'), read_file(output_file)
    )
