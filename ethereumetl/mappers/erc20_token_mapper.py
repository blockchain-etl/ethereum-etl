class EthErc20TokenMapper(object):
    def erc20_token_to_dict(self, erc20_token):
        return {
            'type': 'erc20_token',
            'erc20_token_address': erc20_token.erc20_token_address,
            'erc20_token_symbol': erc20_token.erc20_token_symbol,
            'erc20_token_name': erc20_token.erc20_token_name,
            'erc20_token_decimals': erc20_token.erc20_token_decimals,
            'erc20_token_total_supply': erc20_token.erc20_token_total_supply
        }
