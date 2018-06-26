CREATE EXTERNAL TABLE IF NOT EXISTS parquet_blocks (
    block_number BIGINT,
    block_hash STRING,
    block_parent_hash STRING,
    block_nonce STRING,
    block_sha3_uncles STRING,
    block_logs_bloom STRING,
    block_transactions_root STRING,
    block_state_root STRING,
    block_miner STRING,
    block_difficulty DECIMAL(38,0),
    block_total_difficulty DECIMAL(38,0),
    block_size BIGINT,
    block_extra_data STRING,
    block_gas_limit BIGINT,
    block_gas_used BIGINT,
    block_timestamp BIGINT,
    block_transaction_count BIGINT
)
PARTITIONED BY (start_block BIGINT, end_block BIGINT)
STORED AS PARQUET
LOCATION 's3://<your_bucket>/ethereumetl/parquet/blocks';

MSCK REPAIR TABLE parquet_blocks;