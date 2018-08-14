CREATE EXTERNAL TABLE IF NOT EXISTS receipts (
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
PARTITIONED BY (date STRING)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
    'serialization.format' = ',',
    'field.delim' = ',',
    'escape.delim' = '\\'
)
STORED AS TEXTFILE
LOCATION 's3://<your_bucket>/ethereumetl/export/receipts'
TBLPROPERTIES (
  'skip.header.line.count' = '1'
);

MSCK REPAIR TABLE receipts;
