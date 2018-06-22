class EthBlock(object):
    number = None
    hash = None
    parent_hash = None
    nonce = None
    sha3_uncles = None
    logs_bloom = None
    transactions_root = None
    state_root = None
    miner = None
    difficulty = None
    total_difficulty = None
    size = None
    extra_data = None
    gas_limit = None
    gas_used = None
    timestamp = None

    transactions = []
    transaction_count = None
# 这个文件在定义以太坊区块的成员，transactions_root存的实际是什么呢？transaction_root存的是hash，形如0x1eb26639133d711473edfa15b75c2af3c2b8b6fb7812b881e4285ffe5433c8f5
# 也就是说这个类基本上是区块数据的反映，但是transactons在最终的数据表中是没有的