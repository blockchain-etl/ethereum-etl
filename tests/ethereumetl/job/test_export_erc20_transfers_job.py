import json

import pytest
from web3 import Web3, IPCProvider

import tests.resources
from ethereumetl.job.export_erc20_transfers_job import ExportErc20TransfersJob
from tests.helpers import compare_lines_ignore_order, read_file

RESOURCE_GROUP = 'test_export_erc20_transfers_job'


def read_resource(resource_group, file_name):
    return tests.resources.read_resource([RESOURCE_GROUP, resource_group], file_name)


class MockIPCProvider(IPCProvider):
    def __init__(self, resource_group):
        self.resource_group = resource_group

    def make_request(self, method, params):
        file_name = method + '.json'
        file_content = read_resource(self.resource_group, file_name)
        return json.loads(file_content)


@pytest.mark.parametrize("start_block,end_block,batch_size,resource_group", [
    (483920, 483920, 1, 'block_with_transfers')
])
def test_export_blocks_job(tmpdir, start_block, end_block, batch_size, resource_group):
    output_file = tmpdir.join('erc20_transfers.csv')

    job = ExportErc20TransfersJob(
        start_block=start_block, end_block=end_block, batch_size=batch_size,
        web3=Web3(MockIPCProvider(resource_group)),
        output=output_file
    )
    job.run()

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_erc20_transfers.csv'), read_file(output_file)
    )
