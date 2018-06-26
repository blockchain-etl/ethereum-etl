CREATE EXTERNAL TABLE IF NOT EXISTS transactions (
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
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
    'serialization.format' = ',',
    'field.delim' = ',',
    'escape.delim' = '\\'
)
STORED AS TEXTFILE
LOCATION 's3://<your_bucket>/ethereumetl/export/transactions'
TBLPROPERTIES (
  'skip.header.line.count' = '1'
);

MSCK REPAIR TABLE transactions;