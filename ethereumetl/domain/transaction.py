class EthTransaction(object):
    def __init__(self):
        self.hash: str = None
        self.nonce: int = None
        self.block_hash: str = None
        self.block_number: int = None
        self.index: int = None
        self.from_address: str = None
        self.to_address: str = None
        self.value: int = None
        self.gas: int = None
        self.gas_price: int = None
        self.input: str = None
