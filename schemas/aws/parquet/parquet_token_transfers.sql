CREATE EXTERNAL TABLE IF NOT EXISTS parquet_token_transfers (
    erc20_token STRING,
    erc20_from STRING,
    erc20_to STRING,
    erc20_value DECIMAL(38,0),
    erc20_tx_hash STRING,
    erc20_log_index BIGINT,
    erc20_block_number BIGINT
)
PARTITIONED BY (start_block BIGINT, end_block BIGINT)
STORED AS PARQUET
LOCATION 's3://<your_bucket>/ethereumetl/parquet/token_transfers';

MSCK REPAIR TABLE parquet_token_transfers;