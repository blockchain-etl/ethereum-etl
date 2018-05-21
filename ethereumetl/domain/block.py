from typing import List

from ethereumetl.domain.transaction import EthTransaction


class EthBlock(object):
    def __init__(self):
        self.number: int = None
        self.hash: str = None
        self.parent_hash: str = None
        self.nonce: str = None
        self.sha3_uncles: str = None
        self.logs_bloom: str = None
        self.transactions_root: str = None
        self.state_root: str = None
        self.miner: str = None
        self.difficulty: int = None
        self.total_difficulty: int = None
        self.size: int = None
        self.extra_data: str = None
        self.gas_limit: int = None
        self.gas_used: int = None
        self.timestamp: int = None

        self.transactions: List[EthTransaction] = []
        self.transaction_count: int = 0
