from web3 import HTTPProvider

from ethereumetl.providers.rpc import BatchHTTPProvider
from tests.ethereumetl.job.mock_batch_web3_provider import MockBatchWeb3Provider
from tests.ethereumetl.job.mock_web3_provider import MockWeb3Provider


def get_web3_provider(provider_type, read_resource_lambda=None, batch=False):
    if provider_type == 'mock':
        if read_resource_lambda is None:
            raise ValueError('read_resource_lambda must not be None for provider type mock'.format(provider_type))
        if batch:
            provider = MockBatchWeb3Provider(read_resource_lambda)
        else:
            provider = MockWeb3Provider(read_resource_lambda)
    elif provider_type == 'infura':
        if batch:
            provider = BatchHTTPProvider('https://mainnet.infura.io')
        else:
            provider = HTTPProvider('https://mainnet.infura.io')
    else:
        raise ValueError('Provider type {} is unexpected'.format(provider_type))
    return provider
