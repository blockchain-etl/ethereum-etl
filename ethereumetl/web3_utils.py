from urllib.parse import urlparse

from web3 import IPCProvider, HTTPProvider

DEFAULT_IPC_TIMEOUT = 60


def get_provider_from_uri(uri_string):
    uri = urlparse(uri_string)
    if uri.scheme == 'file':
        return IPCProvider(uri.path, timeout=DEFAULT_IPC_TIMEOUT)
    elif uri.scheme == 'http' or uri.scheme == 'https':
        return HTTPProvider(uri_string)
    else:
        raise ValueError('Unknown uri scheme {}'.format(uri_string))
