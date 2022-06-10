CREATE EXTERNAL TABLE IF NOT EXISTS blocks (
    number BIGINT,
    hash STRING,
    parent_hash STRING,
    nonce STRING,
    sha3_uncles STRING,
    logs_bloom STRING,
    transactions_root STRING,
    state_root STRING,
    receipts_root STRING,
    miner STRING,
    difficulty DECIMAL(38,0),
    total_difficulty DECIMAL(38,0),
    size BIGINT,
    extra_data STRING,
    gas_limit BIGINT,
    gas_used BIGINT,
    timestamp BIGINT,
    transaction_count BIGINT,
    base_fee_per_gas BIGINT
)
PARTITIONED BY (block_date STRING)
ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
LOCATION 's3://<your_bucket>/export/blocks/';

MSCK REPAIR TABLE blocks;
