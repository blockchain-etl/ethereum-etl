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
    transaction_count BIGINT
)
PARTITIONED BY (start_block BIGINT, end_block BIGINT)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
    'serialization.format' = ',',
    'field.delim' = ',',
    'escape.delim' = '\\'
)
STORED AS TEXTFILE
LOCATION 's3://<your_bucket>/ethereumetl/export/blocks'
TBLPROPERTIES (
  'skip.header.line.count' = '1'
);

MSCK REPAIR TABLE blocks;