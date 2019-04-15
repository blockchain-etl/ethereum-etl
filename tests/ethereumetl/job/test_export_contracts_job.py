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
from ethereumetl.jobs.export_contracts_job import ExportContractsJob
from ethereumetl.jobs.exporters.contracts_item_exporter import contracts_item_exporter
from ethereumetl.thread_local_proxy import ThreadLocalProxy
from tests.ethereumetl.job.helpers import get_web3_provider
from tests.helpers import compare_lines_ignore_order, read_file, skip_if_slow_tests_disabled

RESOURCE_GROUP = 'test_export_contracts_job'


def read_resource(resource_group, file_name):
    return tests.resources.read_resource([RESOURCE_GROUP, resource_group], file_name)


CONTRACT_ADDRESSES_UNDER_TEST = ['0x06012c8cf97bead5deae237070f9587f8e7a266d']


@pytest.mark.parametrize("batch_size,contract_addresses,output_format,resource_group,web3_provider_type", [
    (1, CONTRACT_ADDRESSES_UNDER_TEST, 'json', 'erc721_contract', 'mock'),
    skip_if_slow_tests_disabled((1, CONTRACT_ADDRESSES_UNDER_TEST, 'json', 'erc721_contract', 'infura'))
])
def test_export_contracts_job(tmpdir, batch_size, contract_addresses, output_format, resource_group,
                              web3_provider_type):
    contracts_output_file = str(tmpdir.join('actual_contracts.' + output_format))

    job = ExportContractsJob(
        contract_addresses_iterable=contract_addresses,
        batch_size=batch_size,
        batch_web3_provider=ThreadLocalProxy(
            lambda: get_web3_provider(web3_provider_type, lambda file: read_resource(resource_group, file), batch=True)
        ),
        max_workers=5,
        item_exporter=contracts_item_exporter(contracts_output_file)
    )
    job.run()

    print('=====================')
    print(read_file(contracts_output_file))
    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_contracts.' + output_format), read_file(contracts_output_file)
    )
