class EthReceipt(object):
    def __init__(self):
        self.transaction_hash = None
        self.transaction_index = None
        self.block_hash = None
        self.block_number = None
        self.from_address = None
        self.to_address = None
        self.cumulative_gas_used = None
        self.gas_used = None
        self.contract_address = None
        self.logs = []
        self.root = None
        self.status = None
