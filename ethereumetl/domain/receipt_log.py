from typing import List


class EthReceiptLog(object):
    def __init__(self):
        self.log_index: int = None
        self.transaction_hash: str = None
        self.block_hash: str = None
        self.block_number: int = None
        self.address: str = None
        self.data: str = None
        self.topics: List[str] = []
