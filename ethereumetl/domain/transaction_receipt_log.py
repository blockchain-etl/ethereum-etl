class EthReceiptLog(object):
    def __init__(self):
        self.log_index = None
        self.transaction_hash = None
        self.block_hash = None
        self.block_number = None
        self.address = None
        self.data = None
        self.topics = []
