class EntityType:
    BLOCK = 'block'
    BALANCE = 'balance'
    TRANSACTION = 'transaction'
    RECEIPT = 'receipt'
    LOG = 'log'
    TOKEN_TRANSFER = 'token_transfer'
    TRACE = 'trace'
    CONTRACT = 'contract'
    TOKEN = 'token'

    ALL_FOR_STREAMING = [BLOCK, TRANSACTION, BALANCE, LOG, TOKEN_TRANSFER, TRACE, CONTRACT, TOKEN]
    ALL_FOR_INFURA = [BLOCK, TRANSACTION, BALANCE, LOG, TOKEN_TRANSFER]
