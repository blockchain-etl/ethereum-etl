class EthTransactionReceipt(object):
    def __init__(self):
        self.transaction_hash = None
        self.transaction_index = None
        self.block_number = None
        self.block_hash = None
        self.cumulative_gas_used = None
        self.gas_used = None
        self.contract_address = None
        self.logs = None
        self.status = None
