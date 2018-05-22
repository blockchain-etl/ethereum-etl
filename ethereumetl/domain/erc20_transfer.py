class EthErc20Transfer(object):
    def __init__(self):
        self.erc20_token: str = None
        self.erc20_from: str = None
        self.erc20_to: str = None
        self.erc20_value: int = None
        self.erc20_tx_hash: str = None
        self.erc20_block_number: int = None
