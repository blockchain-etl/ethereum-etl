CREATE EXTERNAL TABLE IF NOT EXISTS parquet_transactions (
    hash STRING,
    nonce BIGINT,
    transaction_index BIGINT,
    from_address STRING,
    to_address STRING,
    value DECIMAL(38,0),
    gas BIGINT,
    gas_price BIGINT,
    input STRING,
    receipt_cumulative_gas_used BIGINT,
    receipt_gas_used BIGINT,
    receipt_contract_address STRING,
    receipt_root STRING,
    receipt_status BIGINT,
    block_timestamp TIMESTAMP,
    block_number INTEGER,
    block_hash STRING,
    max_fee_per_gas BIGINT,
    max_priority_fee_per_gas BIGINT,
    transaction_type BIGINT,
    receipt_effective_gas_price BIGINT
)
STORED AS PARQUET
LOCATION 's3://<your_bucket>/ethereumetl/parquet/transactions';
