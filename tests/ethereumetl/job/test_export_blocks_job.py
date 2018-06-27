import json

import pytest

from ethereumetl.jobs.export_blocks_job import ExportBlocksJob
from ethereumetl.jobs.export_blocks_job_item_exporter import export_blocks_job_item_exporter
from ethereumetl.thread_local_proxy import ThreadLocalProxy
from ethereumetl.utils import hex_to_dec
from tests.helpers import compare_lines_ignore_order, read_file
import tests.resources

RESOURCE_GROUP = 'test_export_blocks_job'


def read_resource(resource_group, file_name):
    return tests.resources.read_resource([RESOURCE_GROUP, resource_group], file_name)


class MockIPCWrapper(object):
    def __init__(self, resource_group):
        self.resource_group = resource_group

    def make_request(self, text):
        batch = json.loads(text)
        ipc_response = []
        for req in batch:
            if req['method'] == 'eth_getBlockByNumber':
                block_number = hex_to_dec(req['params'][0])
                file_name = 'ipc_response.block.' + str(block_number) + '.json'
            else:
                tx_hash = req['params'][0]
                file_name = 'ipc_response.receipt.' + str(tx_hash) + '.json'
            file_content = read_resource(self.resource_group, file_name)
            ipc_response.append(json.loads(file_content))
        return ipc_response


@pytest.mark.parametrize("start_block,end_block,batch_size,resource_group", [
    (0, 0, 1, 'block_without_transactions'),
    (47218, 47219, 1, 'blocks_with_transactions'),
    (47218, 47219, 2, 'blocks_with_transactions')
])
def test_export_blocks_job(tmpdir, start_block, end_block, batch_size, resource_group):
    blocks_output_file = tmpdir.join('actual_blocks.csv')
    transactions_output_file = tmpdir.join('actual_transactions.csv')
    receipts_output_file = tmpdir.join('actual_receipts.csv')
    logs_output_file = tmpdir.join('actual_logs.csv')

    job = ExportBlocksJob(
        start_block=start_block, end_block=end_block, batch_size=batch_size,
        ipc_wrapper=ThreadLocalProxy(lambda: MockIPCWrapper(resource_group)),
        max_workers=5,
        item_exporter=export_blocks_job_item_exporter(
            blocks_output_file, transactions_output_file, receipts_output_file
        ),
        export_blocks=blocks_output_file is not None,
        export_transactions=transactions_output_file is not None,
        export_receipts=receipts_output_file is not None,
        export_logs=logs_output_file is not None
    )
    job.run()

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_blocks.csv'), read_file(blocks_output_file)
    )

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_transactions.csv'), read_file(transactions_output_file)
    )

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_receipts.csv'), read_file(receipts_output_file)
    )

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_logs.csv'), read_file(logs_output_file)
    )
