class EthBlock(object):
    def __init__(self):
        self.number = None
        self.hash = None
        self.parent_hash = None
        self.nonce = None
        self.sha3_uncles = None
        self.logs_bloom = None
        self.transactions_root = None
        self.state_root = None
        self.miner = None
        self.difficulty = None
        self.total_difficulty = None
        self.size = None
        self.extra_data = None
        self.gas_limit = None
        self.gas_used = None
        self.timestamp = None

        self.transactions = []
        self.transaction_count = 0
