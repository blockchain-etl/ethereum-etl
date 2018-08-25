CREATE EXTERNAL TABLE IF NOT EXISTS parquet_receipts (
    transaction_hash STRING,
    transaction_index BIGINT,
    block_hash STRING,
    block_number BIGINT,
    cumulative_gas_used BIGINT,
    gas_used BIGINT,
    contract_address STRING,
    root STRING,
    status BIGINT
)
PARTITIONED BY (year STRING, month STRING, day STRING)
STORED AS PARQUET
LOCATION 's3://<your_bucket>/ethereumetl/export/receipts'
TBLPROPERTIES (
  'skip.header.line.count' = '1'
);