CREATE EXTERNAL TABLE IF NOT EXISTS parquet_transactions (
    tx_hash STRING,
    tx_nonce BIGINT,
    tx_block_hash STRING,
    tx_block_number BIGINT,
    tx_index BIGINT,
    tx_from STRING,
    tx_to STRING,
    tx_value DECIMAL(38,0),
    tx_gas BIGINT,
    tx_gas_price BIGINT,
    tx_input STRING
)
PARTITIONED BY (start_block BIGINT, end_block BIGINT)
STORED AS PARQUET
LOCATION 's3://<your_bucket>/ethereumetl/parquet/transactions';

MSCK REPAIR TABLE parquet_transactions;