CREATE EXTERNAL TABLE IF NOT EXISTS logs (
    log_index BIGINT,
    log_transaction_hash STRING,
    log_transaction_index BIGINT,
    log_block_hash STRING,
    log_block_number BIGINT,
    log_address STRING,
    log_data STRING,
    log_topics STRING
)
PARTITIONED BY (start_block BIGINT, end_block BIGINT)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
    'serialization.format' = ',',
    'field.delim' = ',',
    'escape.delim' = '\\'
)
STORED AS TEXTFILE
LOCATION 's3://<your_bucket>/ethereumetl/export/logs'
TBLPROPERTIES (
  'skip.header.line.count' = '1'
);

MSCK REPAIR TABLE blocks;
