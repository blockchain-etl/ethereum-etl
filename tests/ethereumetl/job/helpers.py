from ethereumetl.providers.rpc import BatchHTTPProvider
from ethereumetl.thread_local_proxy import ThreadLocalProxy
from tests.ethereumetl.job.mock_batch_web3_provider import MockBatchWeb3Provider


def get_web3_provider(provider_type, read_resource_lambda=None):
    if provider_type == 'mock':
        if read_resource_lambda is None:
            raise ValueError('read_resource_lambda must not be None for provider type mock'.format(provider_type))
        provider = ThreadLocalProxy(lambda: MockBatchWeb3Provider(read_resource_lambda))
    elif provider_type == 'infura':
        provider = ThreadLocalProxy(lambda: BatchHTTPProvider('https://mainnet.infura.io'))
    else:
        raise ValueError('Provider type {} is unexpected'.format(provider_type))
    return provider
