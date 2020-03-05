# Amazon Athena

## Querying in Amazon Athena

- Upload the files to S3:

```bash
> cd output
> aws s3 sync . s3://<your_bucket>/ethereumetl/export --region ap-southeast-1
```

- Sign in to Athena https://console.aws.amazon.com/athena/home

- Create a database:

```sql
CREATE DATABASE ethereumetl;
```

- Create the tables:
  - blocks: [schemas/aws/blocks.sql](https://github.com/blockchain-etl/ethereum-etl/blob/master/schemas/aws/blocks.sql)
  - transactions: [schemas/aws/transactions.sql](https://github.com/blockchain-etl/ethereum-etl/blob/master/schemas/aws/transactions.sql)
  - token_transfers: [schemas/aws/token_transfers.sql](https://github.com/blockchain-etl/ethereum-etl/blob/master/schemas/aws/token_transfers.sql)
  - contracts: [schemas/aws/contracts.sql](https://github.com/blockchain-etl/ethereum-etl/blob/master/schemas/aws/contracts.sql)
  - receipts: [schemas/aws/receipts.sql](https://github.com/blockchain-etl/ethereum-etl/blob/master/schemas/aws/receipts.sql)
  - logs: [schemas/aws/logs.sql](https://github.com/blockchain-etl/ethereum-etl/blob/master/schemas/aws/logs.sql)
  - tokens: [schemas/aws/tokens.sql](https://github.com/blockchain-etl/ethereum-etl/blob/master/schemas/aws/tokens.sql)

## Airflow DAGs

Refer to https://github.com/medvedev1088/ethereum-etl-airflow for the instructions.

## Tables for Parquet Files

Read [this article](https://medium.com/@medvedev1088/converting-ethereum-etl-files-to-parquet-399e048ddd30) on how to convert CSVs to Parquet.

- Create the tables:
  - parquet_blocks: [schemas/aws/parquet/parquet_blocks.sql](https://github.com/blockchain-etl/ethereum-etl/blob/master/schemas/aws/parquet/parquet_blocks.sql)
  - parquet_transactions: [schemas/aws/parquet/parquet_transactions.sql](https://github.com/blockchain-etl/ethereum-etl/blob/master/schemas/aws/parquet/parquet_transactions.sql)
  - parquet_token_transfers: [schemas/aws/parquet/parquet_token_transfers.sql](https://github.com/blockchain-etl/ethereum-etl/blob/master/schemas/aws/parquet/parquet_token_transfers.sql)

Note that [DECIMAL type is limited to 38 digits in Hive](https://cwiki.apache.org/confluence/display/Hive/LanguageManual+Types#LanguageManualTypes-decimal) so values greater than 38 decimals will be null.