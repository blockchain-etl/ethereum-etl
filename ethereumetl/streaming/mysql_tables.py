from sqlalchemy import Table, Column, Integer, BigInteger, Boolean, String, \
  Numeric, MetaData, VARCHAR, DATETIME
from sqlalchemy.dialects.mysql import LONGTEXT

metadata = MetaData()

# SQL schema is here https://github.com/blockchain-etl/ethereum-etl-postgres/tree/master/schema

BLOCKS = Table(
    'blocks', metadata,
    Column('timestamp', DATETIME),
    Column('number', BigInteger),
    Column('hash', VARCHAR, primary_key=True),
    Column('parent_hash', VARCHAR),
    Column('nonce', VARCHAR),
    Column('sha3_uncles', VARCHAR),
    Column('logs_bloom', VARCHAR),
    Column('transactions_root', VARCHAR),
    Column('state_root', VARCHAR),
    Column('receipts_root', VARCHAR),
    Column('miner', VARCHAR),
    Column('difficulty', Numeric(38)),
    Column('total_difficulty', Numeric(38)),
    Column('size', BigInteger),
    Column('extra_data', VARCHAR),
    Column('gas_limit', BigInteger),
    Column('gas_used', BigInteger),
    Column('transaction_count', BigInteger),
    Column('base_fee_per_gas', BigInteger),
)

TRANSACTIONS = Table(
    'transactions', metadata,
    Column('hash', VARCHAR, primary_key=True),
    Column('nonce', BigInteger),
    Column('transaction_index', BigInteger),
    Column('from_address', VARCHAR),
    Column('to_address', VARCHAR),
    Column('value', Numeric(38)),
    Column('gas', BigInteger),
    Column('gas_price', BigInteger),
    Column('input', LONGTEXT),
    Column('receipt_cumulative_gas_used', BigInteger),
    Column('receipt_gas_used', BigInteger),
    Column('receipt_contract_address', VARCHAR),
    Column('receipt_root', VARCHAR),
    Column('receipt_status', BigInteger),
    Column('block_timestamp', DATETIME),
    Column('block_number', BigInteger),
    Column('block_hash', VARCHAR),
    Column('max_fee_per_gas', BigInteger),
    Column('max_priority_fee_per_gas', BigInteger),
    Column('transaction_type', BigInteger),
    Column('receipt_effective_gas_price', BigInteger),
)

LOGS = Table(
    'logs', metadata,
    Column('log_index', BigInteger, primary_key=True),
    Column('transaction_hash', VARCHAR, primary_key=True),
    Column('transaction_index', BigInteger),
    Column('address', VARCHAR),
    Column('data', VARCHAR),
    Column('topic0', VARCHAR),
    Column('topic1', VARCHAR),
    Column('topic2', VARCHAR),
    Column('topic3', VARCHAR),
    Column('block_timestamp', DATETIME),
    Column('block_number', BigInteger),
    Column('block_hash', VARCHAR),
)

TOKEN_TRANSFERS = Table(
    'token_transfers', metadata,
    Column('token_address', VARCHAR),
    Column('from_address', VARCHAR),
    Column('to_address', VARCHAR),
    Column('value', VARCHAR(78)),
    Column('transaction_hash', VARCHAR, primary_key=True),
    Column('log_index', BigInteger, primary_key=True),
    Column('block_timestamp', DATETIME),
    Column('block_number', BigInteger),
    Column('block_hash', VARCHAR),
)

TRACES = Table(
    'traces', metadata,
    Column('transaction_hash', VARCHAR),
    Column('transaction_index', BigInteger),
    Column('from_address', VARCHAR),
    Column('to_address', VARCHAR),
    Column('value', VARCHAR(78)),
    Column('input', VARCHAR),
    Column('output', VARCHAR),
    Column('trace_type', VARCHAR),
    Column('call_type', VARCHAR),
    Column('reward_type', VARCHAR),
    Column('gas', BigInteger),
    Column('gas_used', BigInteger),
    Column('subtraces', BigInteger),
    Column('trace_address', VARCHAR),
    Column('error', VARCHAR),
    Column('status', Integer),
    Column('block_timestamp', DATETIME),
    Column('block_number', BigInteger),
    Column('block_hash', VARCHAR),
    Column('trace_id', VARCHAR, primary_key=True),
)

TOKENS = Table(
    'tokens', metadata,
    Column('address', VARCHAR(42), primary_key=True),
    Column('name', String),
    Column('symbol', String),
    Column('decimals', Integer),
    Column('function_sighashes', String),
    Column('total_supply', VARCHAR(78)),
    Column('block_number', BigInteger, primary_key=True),
)

CONTRACTS = Table(
    'contracts', metadata,
    Column('address', VARCHAR(42), primary_key=True),
    Column('bytecode', VARCHAR),
    Column('function_sighashes', String),
    Column('is_erc20', Boolean),
    Column('is_erc721', Boolean),
    Column('block_number', BigInteger, primary_key=True),
)
