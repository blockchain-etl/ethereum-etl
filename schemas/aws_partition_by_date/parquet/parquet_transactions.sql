CREATE EXTERNAL TABLE IF NOT EXISTS parquet_transactions (
    hash STRING,
    nonce BIGINT,
    block_hash STRING,
    block_number BIGINT,
    transaction_index BIGINT,
    from_address STRING,
    to_address STRING,
    value DECIMAL(38,0),
    gas BIGINT,
    gas_price BIGINT,
    input STRING
)
PARTITIONED BY (start_block BIGINT, end_block BIGINT)
STORED AS PARQUET
LOCATION 's3://<your_bucket>/ethereumetl/parquet/transactions';

MSCK REPAIR TABLE parquet_transactions;