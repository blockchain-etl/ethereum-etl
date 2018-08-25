CREATE EXTERNAL TABLE IF NOT EXISTS tokens (
    address STRING,
    symbol STRING,
    name STRING,
    decimals BIGINT,
    total_supply DECIMAL(38,0)
)
PARTITIONED BY (year int, month, int, day int)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
    'serialization.format' = ',',
    'field.delim' = ',',
    'escape.delim' = '\\'
)
STORED AS TEXTFILE
LOCATION 's3://<your_bucket>/ethereumetl/export/tokens'
TBLPROPERTIES (
  'skip.header.line.count' = '1'
);

MSCK REPAIR TABLE tokens;
