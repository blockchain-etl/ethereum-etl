CREATE EXTERNAL TABLE IF NOT EXISTS transactions (
    hash STRING,
    nonce BIGINT,
    block_hash STRING,
    block_number BIGINT,
    transaction_index BIGINT,
    from_address STRING,
    to_address STRING,
    value DECIMAL(38,0),
    gas BIGINT,
    gas_price BIGINT,
    input STRING
)
PARTITIONED BY (date STRING)
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