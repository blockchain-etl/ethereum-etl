import copy
import logging

from ethereumetl.providers.auto import get_provider_from_uri
from ethereumetl.utils import parse_provider_uri, pick_provider_uri_move_to_end


class Web3ProviderSelector:
    # TODO: Adjust node selection priority based on node request exception statistics
    def __init__(self, provider_uris_str, max_fail_times=10):
        self.provider_uris_str = provider_uris_str
        self.provider_uri_range = parse_provider_uri(provider_uris_str)
        self.provider_uri_list = copy.copy(self.provider_uri_range)
        self.max_fail_times = max_fail_times
        self.provider_uri = pick_provider_uri_move_to_end(self.provider_uri_list)
        self.batch_web3_provider = get_provider_from_uri(self.provider_uri, batch=True)
        self.provider_dict = self.init_provider_dict()

    def init_provider_dict(self):
        provider_dict = {}
        for uri in self.provider_uri_range:
            provider_dict[uri] = get_provider_from_uri(uri, batch=True)
        return provider_dict

    def select_provider(self):
        provider_uri = pick_provider_uri_move_to_end(self.provider_uri_list)
        logging.info(f'web3 provider using uri: {provider_uri}')
        self.batch_web3_provider = self.get_provider_by_uri(provider_uri)
        return self.batch_web3_provider

    def reset_provider(self):
        self.provider_uri_list = copy.copy(self.provider_uri_range)
        provider_uri = pick_provider_uri_move_to_end(self.provider_uri_list)
        logging.info(f'reset web3 provider using uri: {provider_uri}')
        self.batch_web3_provider = self.get_provider_by_uri(provider_uri)

    def get_provider_by_uri(self, provider_uri):
        if not (provider_uri in self.provider_dict):
            web3_provider = get_provider_from_uri(provider_uri, batch=True)
            self.provider_dict[provider_uri] = web3_provider
        return self.provider_dict[provider_uri]
