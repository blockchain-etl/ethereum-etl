CREATE EXTERNAL TABLE IF NOT EXISTS contracts (
    address STRING,
    bytecode STRING,
    function_sighashes STRING,
    is_erc20 BOOLEAN,
    is_erc721 BOOLEAN
)
PARTITIONED BY (date STRING)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
    'serialization.format' = ',',
    'field.delim' = ',',
    'escape.delim' = '\\'
)
STORED AS TEXTFILE
LOCATION 's3://<your_bucket>/ethereumetl/export/contracts'
TBLPROPERTIES (
  'skip.header.line.count' = '1'
);

MSCK REPAIR TABLE contracts;
