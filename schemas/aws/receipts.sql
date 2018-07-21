CREATE EXTERNAL TABLE IF NOT EXISTS receipts (
    receipt_transaction_hash STRING,
    receipt_transaction_index BIGINT,
    receipt_block_hash STRING,
    receipt_block_number BIGINT,
    receipt_cumulative_gas_used BIGINT,
    receipt_gas_used BIGINT,
    receipt_contract_address STRING,
    receipt_root STRING,
    receipt_status BIGINT
)
PARTITIONED BY (start_block BIGINT, end_block BIGINT)
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

MSCK REPAIR TABLE transactions;
