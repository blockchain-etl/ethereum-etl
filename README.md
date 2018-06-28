# Ethereum ETL

[![Join the chat at https://gitter.im/ethereum-eth](https://badges.gitter.im/ethereum-etl.svg)](https://gitter.im/ethereum-etl/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Build Status](https://travis-ci.org/medvedev1088/ethereum-etl.png)](https://travis-ci.org/medvedev1088/ethereum-etl)

Export blocks and transactions:

```bash
> python export_blocks_and_transactions.py --start-block 0 --end-block 500000 \
--ipc-path ~/Library/Ethereum/geth.ipc --blocks-output blocks.csv --transactions-output transactions.csv
```

Export ERC20 transfers:

```bash
> python export_erc20_transfers.py --start-block 0 --end-block 500000 --ipc-path ~/Library/Ethereum/geth.ipc \
--output erc20_transfers.csv
```

Export ERC20 transfers, filtered by the list of tokens:

```bash
> python export_erc20_transfers.py --start-block 0 --end-block 500000 --ipc-path ~/Library/Ethereum/geth.ipc \
--output erc20_transfers.csv --tokens 0x86fa049857e0209aa7d9e616f7eb3b3b78ecfdb0 0x06012c8cf97bead5deae237070f9587f8e7a266d
```

Read this article https://medium.com/@medvedev1088/exporting-and-analyzing-ethereum-blockchain-f5353414a94e

## Table of Content

- [Schema](#schema)
- [Exporting the Blockchain](#exporting-the-blockchain)
- [Querying in AWS Athena](#querying-in-aws-athena)
- [Querying in GCP BigQuery](#querying-in-gcp-bigquery)


## Schema

`blocks.csv`

Column                  | Type               |
------------------------|---------------------
block_number            | bigint             |
block_hash              | hex_string         |
block_parent_hash       | hex_string         |
block_nonce             | hex_string         |
block_sha3_uncles       | hex_string         |
block_logs_bloom        | hex_string         |
block_transactions_root | hex_string         |
block_state_root        | hex_string         |
block_miner             | address            |
block_difficulty        | numeric            |
block_total_difficulty  | numeric            |
block_size              | bigint             |
block_extra_data        | hex_string         |
block_gas_limit         | bigint             |
block_gas_used          | bigint             |
block_timestamp         | bigint             |
block_transaction_count | bigint             |

`transactions.csv`

Column              |    Type     |
--------------------|--------------
tx_hash             | hex_string  |
tx_nonce            | bigint      |
tx_block_hash       | hex_string  |
tx_block_number     | bigint      |
tx_index            | bigint      |
tx_from             | address     |
tx_to               | address     |
tx_value            | numeric     |
tx_gas              | bigint      |
tx_gas_price        | bigint      |
tx_input            | hex_string  |

`erc20_transfers.csv`

Column              |    Type     |
--------------------|--------------
erc20_token         | address     |
erc20_from          | address     |
erc20_to            | address     |
erc20_value         | numeric     |
erc20_tx_hash       | hex_string  |
erc20_log_index     | bigint      |
erc20_block_number  | bigint      |

`receipts.csv`

Column                       |    Type     |
-----------------------------|--------------
receipt_transaction_hash     | hex_string  |
receipt_transaction_index    | bigint      |
receipt_block_hash           | hex_string  |
receipt_block_number         | bigint      |
receipt_cumulative_gas_used  | bigint      |
receipt_gas_used             | bigint      |
receipt_contract_address     | address     |
receipt_root                 | hex_string  |
receipt_status               | bigint      |

`logs.csv`

Column                       |    Type     |
-----------------------------|--------------
log_index                    | bigint      |
log_transaction_hash         | hex_string  |
log_transaction_index        | bigint      |
log_block_hash               | hex_string  |
log_block_number             | bigint      |
log_address                  | address     |
log_data                     | hex_string  |
log_topics                   | string      |


Note: for the `address` type all hex characters are lower-cased.

## Exporting the Blockchain

1. Install python 3.5+ https://www.python.org/downloads/

1. Install geth https://github.com/ethereum/go-ethereum/wiki/Installing-Geth

1. Start geth. 
Make sure it downloaded the blocks that you need by executing `eth.synching` in the JS console.
You can export blocks below `currentBlock`, 
there is no need to wait until the full sync as the state is not needed.

1. Clone Ethereum ETL and install the dependencies:

    ```bash
    > git clone https://github.com/medvedev1088/ethereum-etl.git
    > cd ethereum-etl
    > pip install -r requirements.txt
    ```

1. Export all:

    ```bash
    > ./export_all.sh -h
    Usage: ./export_all.sh -s <start_block> -e <end_block> -b <batch_size> -i <ipc_path> [-o <output_dir>]
    > ./export_all.sh -s 0 -e 5499999 -b 100000 -i ~/Library/Ethereum/geth.ipc -o output 
    ```
    
    The result will be in the `output` subdirectory, partitioned in Hive style:
   
    ```bash
    output/blocks/start_block=00000000/end_block=00099999/blocks_00000000_00099999.csv
    output/blocks/start_block=00100000/end_block=00199999/blocks_00100000_00199999.csv
    ...
    output/transactions/start_block=00000000/end_block=00099999/transactions_00000000_00099999.csv
    ...
    output/erc20_transfers/start_block=00000000/end_block=00099999/erc20_transfers_00000000_00099999.csv
    ...
    ```

Should work with geth and parity, on Linux, Mac, Windows. 
Tested with Python 3.6, geth 1.8.7, Ubuntu 16.04.4

If you see weird behaviour, e.g. wrong number of rows in the CSV files or corrupted files, 
check this issue: https://github.com/medvedev1088/ethereum-etl/issues/28

#### Reducing the Exporting Time

Read this article https://medium.com/@medvedev1088/how-to-export-the-entire-ethereum-blockchain-to-csv-in-2-hours-for-10-69fef511e9a2

#### Windows

Additional steps:

1. Install Visual C++ Build Tools https://landinghub.visualstudio.com/visual-cpp-build-tools

1. Install Git Bash with  Git for Windows https://git-scm.com/download/win

1. Run in Git Bash:

    ```bash
    >  ./export_all.sh -s 0 -e 999999 -b 100000 -i '\\.\pipe\geth.ipc' -o output 
    ```

#### Command Reference

- Export blocks, transactions, receipts, logs:

```bash
> python export_blocks_and_transactions.py --start-block 0 --end-block 500000 \
--ipc-path ~/Library/Ethereum/geth.ipc --blocks-output blocks.csv --transactions-output transactions.csv
```

Omit `--<entity>-output` options if you don't want to export the corresponding entities.

You can tune `--batch-size`, `--max-workers`, `--ipc-timeout` for performance.

Call `python export_blocks_and_transactions.py -h` for more details. 

- Export ERC20 transfers:

```bash
> python export_erc20_transfers.py --start-block 0 --end-block 500000 \
--ipc-path ~/Library/Ethereum/geth.ipc --batch-size 100 --output erc20_transfers.csv
```

Include `--tokens <token1> <token2>` to filter only certain tokens, e.g.

```bash
> python export_erc20_transfers.py --start-block 0 --end-block 500000 --ipc-path ~/Library/Ethereum/geth.ipc \
--output erc20_transfers.csv --tokens 0x86fa049857e0209aa7d9e616f7eb3b3b78ecfdb0 0x06012c8cf97bead5deae237070f9587f8e7a266d
```

You can tune `--batch-size`, `--max-workers`, `--ipc-timeout` for performance.

Call `python export_erc20_transfers.py -h` for more details. 

#### Running Tests

```bash
> pytest -vv
```

## Querying in AWS Athena

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
  - blocks: [schemas/aws/blocks.sql](schemas/aws/blocks.sql)
  - transactions: [schemas/aws/transactions.sql](schemas/aws/transactions.sql)
  - erc20_transfers: [schemas/aws/erc20_transfers.sql](schemas/aws/erc20_transfers.sql)

### Tables for Parquet Files

Read this article on how to convert CSVs to Parquet https://medium.com/@medvedev1088/converting-ethereum-etl-files-to-parquet-399e048ddd30

- Create the tables:
  - parquet_blocks: [schemas/aws/parquet/parquet_blocks.sql](schemas/aws/parquet/parquet_blocks.sql)
  - parquet_transactions: [schemas/aws/parquet/parquet_transactions.sql](schemas/aws/parquet/parquet_transactions.sql)
  - parquet_erc20_transfers: [schemas/aws/parquet/parquet_erc20_transfers.sql](schemas/aws/parquet/parquet_erc20_transfers.sql)

Note that DECIMAL type is limited to 38 digits in Hive https://cwiki.apache.org/confluence/display/Hive/LanguageManual+Types#LanguageManualTypes-decimal
so values greater than 38 decimals will be null.

## Querying in GCP BigQuery

You can query the data that I exported in the public BigQuery dataset
https://medium.com/@medvedev1088/ethereum-blockchain-on-google-bigquery-283fb300f579

To upload CSVs to BigQuery:

- Install Google Cloud SDK https://cloud.google.com/sdk/docs/quickstart-debian-ubuntu

- Create a new Google Storage bucket https://console.cloud.google.com/storage/browser

- Upload the files:

```bash
> cd output
> gsutil -m rsync -r . gs://<your_bucket>/ethereumetl/export
```

- Sign in to BigQuery https://bigquery.cloud.google.com/ 

- Create a new dataset called `ethereum`

- Load the files from the bucket to BigQuery:

```bash
> cd ethereum-etl
> bq --location=asia-northeast1 load --source_format=CSV --skip_leading_rows=1 ethereum.blocks gs://<your_bucket>/ethereumetl/export/blocks/*.csv ./schemas/gcp/blocks.json
> bq --location=asia-northeast1 load --source_format=CSV --skip_leading_rows=1 ethereum.transactions gs://<your_bucket>/ethereumetl/export/transactions/*.csv ./schemas/gcp/transactions.json
> bq --location=asia-northeast1 load --source_format=CSV --skip_leading_rows=1 --max_bad_records=5000 ethereum.erc20_transfers gs://<your_bucket>/ethereumetl/export/erc20_transfers/*.csv ./schemas/gcp/erc20_transfers.json
```

Note that `--max_bad_records` is needed for erc20_transfers to avoid 
'Error while reading data, error message: Could not parse '68032337690423899710659284523950357745' as numeric for field
erc20_value (position 3) starting at location 52895 numeric overflow' 
for [ERC721](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-721.md) transfers.

### TODOs

1. Unit tests
1. Rewrite export_all.sh in python
1. Add HTTPProvider
1. Error handling and logging

### SQL for Blockchain

I'm currently working on a SaaS solution for analysts and developers. The MVP will have the following:

- Web console for running SQLs based on Redash http://demo.redash.io/
- Built on top of AWS, cost efficient
- Can provide access to raw CSV data if needed
- Support for internal transactions in the future
- Support for API access in the future
- Support for Bitcoin and other blockchains in the future
- ERC20 token metrics in the future

Contact me if you would like to contribute evge.medvedev@gmail.com