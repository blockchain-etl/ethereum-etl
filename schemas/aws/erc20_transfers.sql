CREATE EXTERNAL TABLE IF NOT EXISTS erc20_transfers (
    erc20_token STRING,
    erc20_from STRING,
    erc20_to STRING,
    erc20_value DECIMAL(38,0),
    erc20_tx_hash STRING,
    erc20_log_index BIGINT,
    erc20_block_number BIGINT
)
PARTITIONED BY (start_block BIGINT, end_block BIGINT)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
    'serialization.format' = ',',
    'field.delim' = ',',
    'escape.delim' = '\\'
)
STORED AS TEXTFILE
LOCATION 's3://<your_bucket>/ethereumetl/export/erc20_transfers'
TBLPROPERTIES (
  'skip.header.line.count' = '1'
);

MSCK REPAIR TABLE erc20_transfers;