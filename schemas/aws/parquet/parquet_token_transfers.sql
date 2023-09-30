CREATE EXTERNAL TABLE IF NOT EXISTS parquet_token_transfers (
    token_address STRING,
    from_address STRING,
    to_address STRING,
    value STRING,
    transaction_hash STRING,
    log_index BIGINT,
    block_timestamp TIMESTAMP,
    block_number BIGINT,
    block_hash STRING
)
PARTITIONED BY (start_block BIGINT, end_block BIGINT)
STORED AS PARQUET
LOCATION 's3://<your_bucket>/ethereumetl/parquet/token_transfers';
