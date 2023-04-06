CREATE EXTERNAL TABLE IF NOT EXISTS parquet_token_approvals (
    token_address STRING,
    owner_address STRING,
    spender_address STRING,
    value DECIMAL(38,0),
    transaction_hash STRING,
    log_index BIGINT,
    block_number BIGINT
)
PARTITIONED BY (start_block BIGINT, end_block BIGINT)
STORED AS PARQUET
LOCATION 's3://<your_bucket>/ethereumetl/parquet/token_approvals';

MSCK REPAIR TABLE parquet_token_approvals;