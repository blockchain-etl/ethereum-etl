import json
import os
import threading

import pytest

from ethereumetl.ipc import ThreadLocalIPCWrapper
from ethereumetl.job.export_blocks_job import ExportBlocksJob
from ethereumetl.utils import hex_to_dec
from tests.helpers import compare_files_ignore_line_order


class MockIPCWrapper(object):

    def __init__(self, directory):
        self.directory = directory

    def make_request(self, text):
        batch = json.loads(text)
        ipc_response = []
        for req in batch:
            block_number = hex_to_dec(req['params'][0])
            file_path = os.path.join(self.directory, 'ipc_response.' + str(block_number) + '.json')
            if not os.path.exists(file_path):
                raise ValueError('File does not exist: ' + file_path)
            with open(file_path) as opened_file:
                file_content = opened_file.read()
            ipc_response.append(json.loads(file_content))
        return ipc_response


@pytest.mark.parametrize("start_block,end_block,batch_size,fixture", [
    (0, 0, 1, 'block_without_transactions'),
    (47218, 47219, 1, 'blocks_with_transactions'),
    (47218, 47219, 2, 'blocks_with_transactions')
])
def test_export_blocks_job(tmpdir, request, start_block, end_block, batch_size, fixture):
    file_name = request.module.__file__
    test_dir = os.path.dirname(file_name)
    fixture_dir = os.path.join(test_dir, 'fixtures', fixture)

    if not os.path.isdir(fixture_dir):
        raise ValueError('Not a directory: ' + fixture_dir)

    blocks_output_file = tmpdir.join('actual_blocks.csv')
    transactions_output_file = tmpdir.join('actual_transactions.csv')

    job = ExportBlocksJob(
        start_block=start_block, end_block=end_block, batch_size=batch_size,
        ipc_wrapper=ThreadLocalIPCWrapper(lambda: MockIPCWrapper(str(fixture_dir))),
        blocks_output=blocks_output_file,
        transactions_output=transactions_output_file
    )
    job.run()

    compare_files_ignore_line_order(
        os.path.join(str(fixture_dir), 'expected_blocks.csv'), blocks_output_file)

    compare_files_ignore_line_order(
        os.path.join(str(fixture_dir), 'expected_transactions.csv'), transactions_output_file)
