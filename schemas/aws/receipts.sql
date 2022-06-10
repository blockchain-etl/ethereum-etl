CREATE EXTERNAL TABLE IF NOT EXISTS receipts (
    transaction_hash STRING,
    transaction_index BIGINT,
    block_hash STRING,
    block_number BIGINT,
    cumulative_gas_used BIGINT,
    gas_used BIGINT,
    contract_address STRING,
    root STRING,
    status BIGINT,
    effective_gas_price BIGINT
)
PARTITIONED BY (block_date STRING)
ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
LOCATION 's3://<your_bucket>/export/receipts/';

MSCK REPAIR TABLE receipts;
