import json

import pytest
from web3 import Web3, IPCProvider

import tests.resources
from ethereumetl.jobs.export_erc20_tokens_job import ExportErc20TokensJob
from ethereumetl.jobs.export_erc20_tokens_job_item_exporter import export_erc20_tokens_job_item_exporter
from ethereumetl.thread_local_proxy import ThreadLocalProxy
from tests.helpers import compare_lines_ignore_order, read_file

RESOURCE_GROUP = 'test_export_erc20_tokens_job'


def read_resource(resource_group, file_name):
    return tests.resources.read_resource([RESOURCE_GROUP, resource_group], file_name)


class MockIPCProvider(IPCProvider):
    def __init__(self, resource_group):
        self.resource_group = resource_group

    def make_request(self, method, params):
        if method == 'eth_call':
            to = params[0]['to']
            data = params[0]['data']
            file_name = '{}_{}_{}.json'.format(method, to, data)
        else:
            file_name = method + '.json'
        file_content = read_resource(self.resource_group, file_name)
        return json.loads(file_content)


@pytest.mark.parametrize("token_addresses,resource_group", [
    (['0xf763be8b3263c268e9789abfb3934564a7b80054'], 'token_with_invalid_data')
])
def test_export_erc20_tokens_job(tmpdir, token_addresses, resource_group):
    output_file = tmpdir.join('erc20_tokens.csv')

    job = ExportErc20TokensJob(
        token_addresses_iterable=token_addresses,
        web3=ThreadLocalProxy(lambda: Web3(MockIPCProvider(resource_group))),
        item_exporter=export_erc20_tokens_job_item_exporter(output_file),
        max_workers=5
    )
    job.run()

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_erc20_tokens.csv'), read_file(output_file)
    )
