CREATE EXTERNAL TABLE IF NOT EXISTS logs (
    log_index BIGINT,
    transaction_hash STRING,
    transaction_index BIGINT,
    block_hash STRING,
    block_number BIGINT,
    address STRING,
    data STRING,
    topics STRING
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

MSCK REPAIR TABLE logs;
