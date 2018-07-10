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
> python export_erc20_transfers.py --start-block 0 --end-block 500000 \
--ipc-path ~/Library/Ethereum/geth.ipc --output erc20_transfers.csv
```

Export receipts and logs (Follow [Command Reference](#command-reference)):

```bash
> python export_receipts_and_logs.py --tx-hashes tx_hashes.csv \
--ipc-path ~/Library/Ethereum/geth.ipc --receipts-output receipts.csv --logs-output logs.csv
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

Column                  | Type               | Description |
------------------------|--------------------|--------------
block_number            | bigint             | The block number |
block_hash              | hex_string         | Hash of the block |
block_parent_hash       | hex_string         | Hash of the parent block |
block_nonce             | hex_string         | Hash of the generated proof-of-work |
block_sha3_uncles       | hex_string         | SHA3 of the uncles data in the block |
block_logs_bloom        | hex_string         | The bloom filter for the logs of the block. null when its pending block |
block_transactions_root | hex_string         | The root of the transaction trie of the block |
block_state_root        | hex_string         | The root of the final state trie of the block |
block_miner             | address            | The address of the beneficiary to whom the mining rewards were given |
block_difficulty        | numeric            | Integer of the difficulty for this block |
block_total_difficulty  | numeric            | Integer of the total difficulty of the chain until this block |
block_size              | bigint             | The size of this block in bytes |
block_extra_data        | hex_string         | The extra data field of this block |
block_gas_limit         | bigint             | The maximum gas allowed in this block |
block_gas_used          | bigint             | The total used gas by all transactions in this block |
block_timestamp         | bigint             | The unix timestamp for when the block was collated |
block_transaction_count | bigint             | The number of transactions in the block |

### transactions.csv

Column              |    Type     | Description |
--------------------|-------------|--------------
tx_hash             | hex_string  | Hash of the transaction |
tx_nonce            | bigint      | The number of transactions made by the sender prior to this one |
tx_block_hash       | hex_string  | Hash of the block where this transaction was in. null when its pending |
tx_block_number     | bigint      | Block number where this transaction was in. null when its pending |
tx_index            | bigint      | Integer of the transactions index position in the block. null when its pending |
tx_from             | address     | Address of the sender |
tx_to               | address     | Address of the receiver. null when its a contract creation transaction |
tx_value            | numeric     | Value transferred in Wei |
tx_gas              | bigint      | Gas provided by the sender |
tx_gas_price        | bigint      | Gas price provided by the sender in Wei |
tx_input            | hex_string  | The data send along with the transaction |

### erc20_transfers.csv

Column              |    Type     | Description |
--------------------|-------------|--------------
erc20_token         | address     | ERC20 token address |
erc20_from          | address     | Address of the sender |
erc20_to            | address     | Address of the receiver |
erc20_value         | numeric     | Value transferred |
erc20_tx_hash       | hex_string  | Transaction hash |
erc20_log_index     | bigint      | Log index in the transaction receipt |
erc20_block_number  | bigint      | The block number |

### receipts.csv

Column                       |    Type     | Description |
-----------------------------|-------------|--------------
receipt_transaction_hash     | hex_string  | Hash of the transaction |
receipt_transaction_index    | bigint      | Integer of the transactions index position in the block |
receipt_block_hash           | hex_string  | Hash of the block where this transaction was in |
receipt_block_number         | bigint      | Block number where this transaction was in |
receipt_cumulative_gas_used  | bigint      | The total amount of gas used when this transaction was executed in the block |
receipt_gas_used             | bigint      | The amount of gas used by this specific transaction alone |
receipt_contract_address     | address     | The contract address created, if the transaction was a contract creation, otherwise null |
receipt_root                 | hex_string  | 32 bytes of post-transaction stateroot (pre Byzantium) |
receipt_status               | bigint      | Either 1 (success) or 0 (failure) |

### logs.csv

Column                       |    Type     | Description |
-----------------------------|-------------|--------------
log_index                    | bigint      | Integer of the log index position in the block. null when its pending log |
log_transaction_hash         | hex_string  | Hash of the transactions this log was created from. null when its pending log |
log_transaction_index        | bigint      | Integer of the transactions index position log was created from |
log_block_hash               | hex_string  | Hash of the block where this log was in. null when its pending |
log_block_number             | bigint      | The block number where this log was in |
log_address                  | address     | Address from which this log originated |
log_data                     | hex_string  | Contains one or more 32 Bytes non-indexed arguments of the log |
log_topics                   | string      | Pipe-separated (&#124; character) string of indexed log arguments (0 to 4 32-byte hex strings). (In solidity: The first topic is the hash of the signature of the event (e.g. Deposit(address,bytes32,uint256)), except you declared the event with the anonymous specifier.) |

### contracts.csv

Column                       |    Type     | Description |
-----------------------------|-------------|--------------
contract_address             | address     | Address of the contract |
contract_bytecode            | hex_string  | Bytecode of the contract |

### erc20_tokens.csv

Column                       |    Type     | Description |
-----------------------------|-------------|--------------
erc20_token_address          | address     | The address of the ERC20 token |
erc20_token_symbol           | string      | The symbol of the ERC20 token |
erc20_token_name             | string      | The name of the ERC20 token |
erc20_token_decimals         | bigint      | The number of decimals the token uses - e.g. 8, means to divide the token amount by 100000000 to get its user representation |
erc20_token_total_supply     | numeric     | The total token supply |

Note: for `erc20_token_symbol`, `erc20_token_name`, `erc20_token_decimals`, `erc20_token_total_supply` 
columns in `erc20_tokens.csv` the values starting with `Error: ` mean the corresponding ERC20 function call
resulted in an error, e.g. `Error: BadFunctionCallOutput - Could not decode contract function call symbol return data b'' for output_types ['string']`

Note: for the `address` type all hex characters are lower-cased.

## Exporting the Blockchain

1. Install python 3.5+ https://www.python.org/downloads/

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
    >  ./export_all.sh -s 0 -e 999999 -b 100000 -i '\\.\pipe\geth.ipc' -o output
    ```

#### Command Reference

##### export_blocks_and_transactions.py

```bash
> python export_blocks_and_transactions.py --start-block 0 --end-block 500000 \
--ipc-path ~/Library/Ethereum/geth.ipc --blocks-output blocks.csv --transactions-output transactions.csv
```

Omit `--blocks-output` or `--transactions-output` options if you want to export only transactions/blocks.

You can tune `--batch-size`, `--max-workers`, `--ipc-timeout` for performance.

Call `python export_blocks_and_transactions.py -h` for more details.

##### export_erc20_transfers.py

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

##### export_receipts_and_logs.py

First extract transaction hashes from `transactions.csv`:

```bash
> python extract_csv_column.py --input transactions.csv --column tx_hash --output tx_hashes.csv
```

Then export receipts and logs:

```bash
> python export_receipts_and_logs.py --tx-hashes tx_hashes.csv \
--ipc-path ~/Library/Ethereum/geth.ipc --receipts-output receipts.csv --logs-output logs.csv
```

Omit `--receipts-output` or `--logs-output` options if you want to export only logs/receipts.

You can tune `--batch-size`, `--max-workers`, `--ipc-timeout` for performance.

Call `python export_receipts_and_logs.py -h` for more details.

Upvote this feature request https://github.com/ethereum/go-ethereum/issues/17044,
it will make receipts and logs export much faster.


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
> bq --location=US load --replace --source_format=CSV --skip_leading_rows=1 --max_bad_records=5000 ethereum.erc20_transfers gs://<your_bucket>/ethereumetl/export/erc20_transfers/*.csv ./schemas/gcp/erc20_transfers.json
> bq --location=US load --replace --source_format=CSV --skip_leading_rows=1 ethereum.receipts gs://<your_bucket>/ethereumetl/export/receipts/*.csv ./schemas/gcp/receipts.json
> bq --location=US load --replace --source_format=CSV --skip_leading_rows=1 ethereum.logs gs://<your_bucket>/ethereumetl/export/logs/*.csv ./schemas/gcp/logs.json
> bq --location=US load --replace --source_format=CSV --skip_leading_rows=1 ethereum.contracts gs://<your_bucket>/ethereumetl/export/contracts/*.csv ./schemas/gcp/contracts.json
```

Note that `--max_bad_records` is needed for erc20_transfers to avoid
'Error while reading data, error message: Could not parse '68032337690423899710659284523950357745' as numeric for field
erc20_value (position 3) starting at location 52895 numeric overflow'
for [ERC721](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-721.md) transfers.

```bash
> bq mk --table --description "Exported using https://github.com/medvedev1088/ethereum-etl" --time_partitioning_field block_timestamp_partition ethereumetl:ethereum.transactions_join_receipts ./schemas/gcp/transactions_join_receipts.json
> SELECT_SQL=$(cat ./schemas/gcp/transactions_join_receipts.sql | tr '\n' ' ')
> bq --location=US query --replace --destination_table ethereumetl:ethereum.transactions_join_receipts --use_legacy_sql=false "$SELECT_SQL"
```

### Public Dataset

You can query the data that I exported in the public BigQuery dataset
https://medium.com/@medvedev1088/ethereum-blockchain-on-google-bigquery-283fb300f579

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
