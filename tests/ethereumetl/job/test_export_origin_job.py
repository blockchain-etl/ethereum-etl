import pytest
import tests.resources

from web3 import Web3

import tests.resources

from tests.ethereumetl.job.mock_ipfs_client import MockIpfsClient
from tests.ethereumetl.job.helpers import get_web3_provider
from tests.helpers import compare_lines_ignore_order, read_file, skip_if_slow_tests_disabled

from ethereumetl.jobs.export_origin_job import ExportOriginJob
from ethereumetl.jobs.exporters.origin_exporter import origin_marketplace_listing_item_exporter, origin_shop_product_item_exporter
from ethereumetl.ipfs.origin import get_origin_ipfs_client
from ethereumetl.thread_local_proxy import ThreadLocalProxy

RESOURCE_GROUP = 'test_export_origin_job'

def read_resource(resource_group, file_name):
    return tests.resources.read_resource([RESOURCE_GROUP, resource_group], file_name)


@pytest.mark.parametrize("start_block,end_block,batch_size,output_format,resource_group,web3_provider_type,ipfs_client_type", [
    (10014847, 10014847, 1, 'json', 'blocks_with_logs', 'mock', 'mock'),
    skip_if_slow_tests_disabled((10014847, 10014847, 1, 'json', 'blocks_with_logs', 'infura', 'ipfs'))
])
def test_export_origin(tmpdir, start_block, end_block, batch_size, output_format, resource_group, web3_provider_type, ipfs_client_type):
    marketplace_output_file = str(tmpdir.join('actual_marketplace.' + output_format))
    shop_output_file = str(tmpdir.join('actual_shop.' + output_format))

    ipfs_client = MockIpfsClient(lambda file: read_resource(resource_group, file)) if ipfs_client_type == 'mock' else get_origin_ipfs_client()

    job = ExportOriginJob(
        start_block=start_block,
        end_block=end_block,
        batch_size=batch_size,
        web3=ThreadLocalProxy(
            lambda: Web3(get_web3_provider(web3_provider_type, lambda file: read_resource(resource_group, file)))
        ),
        ipfs_client=ipfs_client,
        marketplace_listing_exporter=origin_marketplace_listing_item_exporter(marketplace_output_file),
        shop_product_exporter=origin_shop_product_item_exporter(shop_output_file),
        max_workers=5)

    job.run()

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_marketplace.' + output_format), read_file(marketplace_output_file)
    )

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_shop.' + output_format), read_file(shop_output_file)
    )
