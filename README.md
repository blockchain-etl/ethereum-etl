# Ethereum ETL

[![Join the chat at https://gitter.im/ethereum-eth](https://badges.gitter.im/ethereum-etl.svg)](https://gitter.im/ethereum-etl/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Build Status](https://travis-ci.org/medvedev1088/ethereum-etl.png)](https://travis-ci.org/medvedev1088/ethereum-etl)

Export blocks and transactions ([Reference](#export_blocks_and_transactionspy)):

```bash
> python export_blocks_and_transactions.py --start-block 0 --end-block 500000 \
--provider-uri https://mainnet.infura.io/ --blocks-output blocks.csv --transactions-output transactions.csv
```

Export ERC20 transfers ([Reference](#export_erc20_transferspy)):

```bash
> python export_erc20_transfers.py --start-block 0 --end-block 500000 \
--provider-uri file://$HOME/Library/Ethereum/geth.ipc --output erc20_transfers.csv
```

Export receipts and logs ([Reference](#export_receipts_and_logspy)):

```bash
> python export_receipts_and_logs.py --tx-hashes tx_hashes.csv \
--provider-uri https://mainnet.infura.io/ --receipts-output receipts.csv --logs-output logs.csv
```

Read this article https://medium.com/@medvedev1088/exporting-and-analyzing-ethereum-blockchain-f5353414a94e

## Table of Contents

- [Schema](#schema)
  - [blocks.csv](#blockscsv)
  - [transactions.csv](#transactionscsv)
  - [erc20_transfers.csv](#erc20_transferscsv)
  - [receipts.csv](#receiptscsv)
  - [logs.csv](#logscsv)
  - [contracts.csv](#contractscsv)
  - [erc20_tokens.csv](#erc20_tokenscsv)
- [Exporting the Blockchain](#exporting-the-blockchain)
  - [Export in 2 Hours](#export-in-2-hours)
  - [Command Reference](#command-reference)
- [Querying in Amazon Athena](#querying-in-amazon-athena)
- [Querying in Google BigQuery](#querying-in-google-bigquery)
  - [Public Dataset](#public-dataset)


## Schema

### blocks.csv

Column                  | Type               |
------------------------|--------------------|
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

### transactions.csv

Column              |    Type     |
--------------------|-------------|
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

### erc20_transfers.csv

Column              |    Type     |
--------------------|-------------|
erc20_token         | address     |
erc20_from          | address     |
erc20_to            | address     |
erc20_value         | numeric     |
erc20_tx_hash       | hex_string  |
erc20_log_index     | bigint      |
erc20_block_number  | bigint      |

### receipts.csv

Column                       |    Type     |
-----------------------------|-------------|
receipt_transaction_hash     | hex_string  |
receipt_transaction_index    | bigint      |
receipt_block_hash           | hex_string  |
receipt_block_number         | bigint      |
receipt_cumulative_gas_used  | bigint      |
receipt_gas_used             | bigint      |
receipt_contract_address     | address     |
receipt_root                 | hex_string  |
receipt_status               | bigint      |

### logs.csv

Column                       |    Type     |
-----------------------------|-------------|
log_index                    | bigint      |
log_transaction_hash         | hex_string  |
log_transaction_index        | bigint      |
log_block_hash               | hex_string  |
log_block_number             | bigint      |
log_address                  | address     |
log_data                     | hex_string  |
log_topics                   | string      |

### contracts.csv

Column                       |    Type     |
-----------------------------|-------------|
contract_address             | address     |
contract_bytecode            | hex_string  |
contract_function_sighashes  | string      |
contract_is_erc20            | boolean     |
contract_is_erc721           | boolean     |

### erc20_tokens.csv

Column                       |    Type     |
-----------------------------|-------------|
erc20_token_address          | address     |
erc20_token_symbol           | string      |
erc20_token_name             | string      |
erc20_token_decimals         | bigint      |
erc20_token_total_supply     | numeric     |

You can find column descriptions in [schemas/gcp](schemas/gcp)

Note: `erc20_token_symbol`, `erc20_token_name`, `erc20_token_decimals`, `erc20_token_total_supply` 
columns in `erc20_tokens.csv` can have empty values in case the contract doesn't implement the corresponding methods
or implements it incorrectly (e.g. wrong return type). 

Note: for the `address` type all hex characters are lower-cased. 
`boolean` type can have 2 values: `True` or `False`.

## Exporting the Blockchain

1. Install python 3.5 or 3.6 https://www.python.org/downloads/

1. You can use Infura if you don't need ERC20 transfers (Infura doesn't support eth_getFilterLogs JSON RPC method).
For that use `-p https://mainnet.infura.io/` option for the commands below. If you need ERC20 transfers or want to
export the data ~40 times faster, you will need to set up a local Ethereum node:

1. Install geth https://github.com/ethereum/go-ethereum/wiki/Installing-Geth

1. Start geth.
Make sure it downloaded the blocks that you need by executing `eth.syncing` in the JS console.
You can export blocks below `currentBlock`, 
there is no need to wait until the full sync as the state is not needed (unless you also need contracts bytecode 
and token details).
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
    Usage: ./export_all.sh -s <start_block> -e <end_block> -b <batch_size> -p <provider_uri> [-o <output_dir>]
    > ./export_all.sh -s 0 -e 5499999 -b 100000 -p file://$HOME/Library/Ethereum/geth.ipc -o output
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

If you see weird behavior, e.g. wrong number of rows in the CSV files or corrupted files,
check this issue: https://github.com/medvedev1088/ethereum-etl/issues/28

#### Export in 2 Hours

You can use AWS Auto Scaling and Data Pipeline to reduce the exporting time to a few hours.
Read this article for details https://medium.com/@medvedev1088/how-to-export-the-entire-ethereum-blockchain-to-csv-in-2-hours-for-10-69fef511e9a2

#### Running in Windows

Additional steps:

1. Install Visual C++ Build Tools https://landinghub.visualstudio.com/visual-cpp-build-tools

1. Install Git Bash with  Git for Windows https://git-scm.com/download/win

1. Run in Git Bash:

    ```bash
    >  ./export_all.sh -s 0 -e 999999 -b 100000 -p 'file:\\\\.\pipe\geth.ipc' -o output
    ```

#### Command Reference

- [export_blocks_and_transactions.py](#export_blocks_and_transactionspy)
- [export_erc20_transfers.py](#export_erc20_transferspy)
- [extract_erc20_transfers.py](#extract_erc20_transferspy)
- [export_receipts_and_logs.py](#export_receipts_and_logspy)
- [export_contracts.py](#export_contractspy)
- [export_erc20_tokens.py](#export_erc20_tokenspy)
- [get_block_range_for_date.py](#get_block_range_for_datepy)

All the commands accept `-h` parameter for help, e.g.:

```bash
> python export_blocks_and_transactions.py -h

usage: export_blocks_and_transactions.py [-h] [-s START_BLOCK] -e END_BLOCK
                                         [-b BATCH_SIZE] --provider-uri PROVIDER_URI
                                         [-w MAX_WORKERS]
                                         [--blocks-output BLOCKS_OUTPUT]
                                         [--transactions-output TRANSACTIONS_OUTPUT]

Export blocks and transactions.
```

For the `--output` parameters the supported types are csv and json. The format type is inferred from the output file name.

##### export_blocks_and_transactions.py

```bash
> python export_blocks_and_transactions.py --start-block 0 --end-block 500000 \
--provider-uri file://$HOME/Library/Ethereum/geth.ipc --blocks-output blocks.csv --transactions-output transactions.csv
```

Omit `--blocks-output` or `--transactions-output` options if you want to export only transactions/blocks.

You can tune `--batch-size`, `--max-workers` for performance.

##### export_erc20_transfers.py

The API used in this command is not supported by Infura, so you will need a local node. 
If you want to use Infura for exporting ERC20 transfers refer to [extract_erc20_transfers.py](#extract_erc20_transferspy)

```bash
> python export_erc20_transfers.py --start-block 0 --end-block 500000 \
--provider-uri file://$HOME/Library/Ethereum/geth.ipc --batch-size 100 --output erc20_transfers.csv
```

Include `--tokens <token1> <token2>` to filter only certain tokens, e.g.

```bash
> python export_erc20_transfers.py --start-block 0 --end-block 500000 --provider-uri file://$HOME/Library/Ethereum/geth.ipc \
--output erc20_transfers.csv --tokens 0x86fa049857e0209aa7d9e616f7eb3b3b78ecfdb0 0x06012c8cf97bead5deae237070f9587f8e7a266d
```

You can tune `--batch-size`, `--max-workers` for performance.

##### export_receipts_and_logs.py

First extract transaction hashes from `transactions.csv` 
(Exported with [export_blocks_and_transactions.py](#export_blocks_and_transactionspy)):

```bash
> python extract_csv_column.py --input transactions.csv --column tx_hash --output tx_hashes.csv
```

Then export receipts and logs:

```bash
> python export_receipts_and_logs.py --tx-hashes tx_hashes.csv \
--provider-uri file://$HOME/Library/Ethereum/geth.ipc --receipts-output receipts.csv --logs-output logs.csv
```

Omit `--receipts-output` or `--logs-output` options if you want to export only logs/receipts.

You can tune `--batch-size`, `--max-workers` for performance.

Upvote this feature request https://github.com/paritytech/parity/issues/9075,
it will make receipts and logs export much faster.

##### extract_erc20_transfers.py

First export receipt logs with [export_receipts_and_logs.py](#export_receipts_and_logspy).

Then extract transfers from the logs.csv file:

```bash
> python extract_erc20_transfers.py --logs logs.csv --output erc20_transfers.csv
```

You can tune `--batch-size`, `--max-workers` for performance.

##### export_contracts.py

First extract contract addresses from `receipts.csv`
(Exported with [export_receipts_and_logs.py](#export_receipts_and_logspy)):

```bash
> python extract_csv_column.py --input receipts.csv --column receipt_contract_address --output contract_addresses.csv
```

Then export contracts:

```bash
> python export_contracts.py --contract-addresses contract_addresses.csv \
--provider-uri file://$HOME/Library/Ethereum/geth.ipc --output contracts.csv
```

You can tune `--batch-size`, `--max-workers` for performance.

##### export_erc20_tokens.py

First extract token addresses from `erc20_transfers.csv` 
(Exported with [export_erc20_transfers.py](#export_erc20_transferspy)):

```bash
> python extract_csv_column.py -i erc20_transfers.csv -c erc20_token -o - | sort | uniq > erc20_token_addresses.csv
```

Then export ERC20 tokens:

```bash
> python export_erc20_tokens.py --token-addresses erc20_token_addresses.csv \
--provider-uri file://$HOME/Library/Ethereum/geth.ipc --output erc20_tokens.csv
```

You can tune `--max-workers` for performance.

Note that there will be duplicate tokens across different partitions, 
which need to be deduplicated (see Querying in Google BigQuery section).

Upvote this pull request to make erc20_tokens export faster 
https://github.com/ethereum/web3.py/pull/944#issuecomment-403957468

##### get_block_range_for_date.py

```bash
> python get_block_range_for_date.py --provider-uri=https://mainnet.infura.io/ --date 2018-01-01
4832686,4838611
```

#### Running Tests

```bash
> pytest -vv
```

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
  - blocks: [schemas/aws/blocks.sql](schemas/aws/blocks.sql)
  - transactions: [schemas/aws/transactions.sql](schemas/aws/transactions.sql)
  - erc20_transfers: [schemas/aws/erc20_transfers.sql](schemas/aws/erc20_transfers.sql)
  - contracts: [schemas/aws/contracts.sql](schemas/aws/contracts.sql)
  - receipts: [schemas/aws/receipts.sql](schemas/aws/receipts.sql)
  - logs: [schemas/aws/logs.sql](schemas/aws/logs.sql)
  - erc20_tokens: [schemas/aws/erc20_tokens.sql](schemas/aws/erc20_tokens.sql)

### Tables for Parquet Files

Read this article on how to convert CSVs to Parquet https://medium.com/@medvedev1088/converting-ethereum-etl-files-to-parquet-399e048ddd30

- Create the tables:
  - parquet_blocks: [schemas/aws/parquet/parquet_blocks.sql](schemas/aws/parquet/parquet_blocks.sql)
  - parquet_transactions: [schemas/aws/parquet/parquet_transactions.sql](schemas/aws/parquet/parquet_transactions.sql)
  - parquet_erc20_transfers: [schemas/aws/parquet/parquet_erc20_transfers.sql](schemas/aws/parquet/parquet_erc20_transfers.sql)

Note that DECIMAL type is limited to 38 digits in Hive https://cwiki.apache.org/confluence/display/Hive/LanguageManual+Types#LanguageManualTypes-decimal
so values greater than 38 decimals will be null.

## Querying in Google BigQuery

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
> bq --location=US load --replace --source_format=CSV --skip_leading_rows=1 ethereum.blocks gs://<your_bucket>/ethereumetl/export/blocks/*.csv ./schemas/gcp/blocks.json
> bq --location=US load --replace --source_format=CSV --skip_leading_rows=1 ethereum.transactions gs://<your_bucket>/ethereumetl/export/transactions/*.csv ./schemas/gcp/transactions.json
> bq --location=US load --replace --source_format=CSV --skip_leading_rows=1 ethereum.erc20_transfers gs://<your_bucket>/ethereumetl/export/erc20_transfers/*.csv ./schemas/gcp/erc20_transfers.json
> bq --location=US load --replace --source_format=CSV --skip_leading_rows=1 ethereum.receipts gs://<your_bucket>/ethereumetl/export/receipts/*.csv ./schemas/gcp/receipts.json
> bq --location=US load --replace --source_format=NEWLINE_DELIMITED_JSON ethereum.logs gs://<your_bucket>/ethereumetl/export/logs/*.json ./schemas/gcp/logs.json
> bq --location=US load --replace --source_format=NEWLINE_DELIMITED_JSON ethereum.contracts gs://<your_bucket>/ethereumetl/export/contracts/*.json ./schemas/gcp/contracts.json
> bq --location=US load --replace --source_format=CSV --skip_leading_rows=1 --allow_quoted_newlines ethereum.erc20_tokens_duplicates gs://<your_bucket>/ethereumetl/export/erc20_tokens/*.csv ./schemas/gcp/erc20_tokens.json
```

Note that NEWLINE_DELIMITED_JSON is used to support REPEATED mode for the columns with lists.

Join `transactions` and `receipts`:

```bash
> bq mk --table --description "Exported using https://github.com/medvedev1088/ethereum-etl" --time_partitioning_field block_timestamp_partition ethereum.transactions_join_receipts ./schemas/gcp/transactions_join_receipts.json
> bq --location=US query --replace --destination_table ethereum.transactions_join_receipts --use_legacy_sql=false "$(cat ./schemas/gcp/transactions_join_receipts.sql | tr '\n' ' ')"
```

Deduplicate `erc20_tokens`:

```bash
> bq mk --table --description "Exported using https://github.com/medvedev1088/ethereum-etl" ethereum.erc20_tokens ./schemas/gcp/erc20_tokens.json
> bq --location=US query --replace --destination_table ethereum.erc20_tokens --use_legacy_sql=false "$(cat ./schemas/gcp/erc20_tokens_deduplicate.sql | tr '\n' ' ')"
```

### Public Dataset

You can query the data that I exported in the public BigQuery dataset
https://medium.com/@medvedev1088/ethereum-blockchain-on-google-bigquery-283fb300f579

### SQL for Blockchain

I'm currently working on a SaaS solution for analysts and developers. The MVP will have the following:

- Built on top of AWS, cost efficient
- Can provide access to raw CSV data if needed
- Support for internal transactions in the future
- Support for Bitcoin and other blockchains in the future
- ERC20 token metrics in the future

Contact me if you would like to contribute evge.medvedev@gmail.com
