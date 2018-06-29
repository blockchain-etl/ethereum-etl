import pytest

import tests.resources
from ethereumetl.jobs.export_receipts_job import ExportReceiptsJob
from ethereumetl.jobs.export_receipts_job_item_exporter import export_receipts_job_item_exporter
from ethereumetl.thread_local_proxy import ThreadLocalProxy
from tests.ethereumetl.job.mock_ipc_wrapper import MockIPCWrapper
from tests.helpers import compare_lines_ignore_order, read_file

RESOURCE_GROUP = 'test_export_receipts_job'


def read_resource(resource_group, file_name):
    return tests.resources.read_resource([RESOURCE_GROUP, resource_group], file_name)


@pytest.mark.parametrize("batch_size,resource_group", [
    (1, 'receipts_with_logs'),
    (2, 'receipts_with_logs')
])
def test_export_blocks_job(tmpdir, batch_size, resource_group):
    receipts_output_file = tmpdir.join('actual_receipts.csv')
    logs_output_file = tmpdir.join('actual_logs.csv')

    job = ExportReceiptsJob(
        tx_hashes_iterable=['0x04cbcb236043d8fb7839e07bbc7f5eed692fb2ca55d897f1101eac3e3ad4fab8',
                            '0x463d53f0ad57677a3b430a007c1c31d15d62c37fab5eee598551697c297c235c',
                            '0x05287a561f218418892ab053adfb3d919860988b19458c570c5c30f51c146f02',
                            '0xcea6f89720cc1d2f46cc7a935463ae0b99dd5fad9c91bb7357de5421511cee49'],
        batch_size=batch_size,
        ipc_wrapper=ThreadLocalProxy(lambda: MockIPCWrapper(lambda file: read_resource(resource_group, file))),
        max_workers=5,
        item_exporter=export_receipts_job_item_exporter(receipts_output_file, logs_output_file),
        export_receipts=receipts_output_file is not None,
        export_logs=logs_output_file is not None
    )
    job.run()

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_receipts.csv'), read_file(receipts_output_file)
    )

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_logs.csv'), read_file(logs_output_file)
    )
