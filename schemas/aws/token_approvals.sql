CREATE EXTERNAL TABLE IF NOT EXISTS token_approvals (
    token_address STRING,
    spender_address STRING,
    spender_address STRING,
    value STRING,
    transaction_hash STRING,
    log_index BIGINT,
    block_number BIGINT
)
PARTITIONED BY (block_date STRING)
ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
LOCATION 's3://<your_bucket>/export/token_approvals/';

MSCK REPAIR TABLE token_approvals;
