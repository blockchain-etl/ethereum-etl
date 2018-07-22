CREATE EXTERNAL TABLE IF NOT EXISTS erc20_tokens (
    erc20_token_address STRING,
    erc20_token_symbol STRING,
    erc20_token_name STRING,
    erc20_token_decimals BIGINT,
    erc20_token_total_supply DECIMAL(38,0)
)
PARTITIONED BY (start_block BIGINT, end_block BIGINT)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
    'serialization.format' = ',',
    'field.delim' = ',',
    'escape.delim' = '\\'
)
STORED AS TEXTFILE
LOCATION 's3://<your_bucket>/ethereumetl/export/erc20_tokens'
TBLPROPERTIES (
  'skip.header.line.count' = '1'
);

MSCK REPAIR TABLE erc20_tokens;
