# Ethereum ETL

[![Join the chat at https://gitter.im/ethereum-eth](https://badges.gitter.im/ethereum-etl.svg)](https://gitter.im/ethereum-etl/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Build Status](https://travis-ci.org/medvedev1088/ethereum-etl.png)](https://travis-ci.org/medvedev1088/ethereum-etl)

Export blocks and transactions ([Schema](#blockscsv), [Reference](#export_blocks_and_transactionspy)):

```bash
> python export_blocks_and_transactions.py --start-block 0 --end-block 500000 \
--provider-uri https://mainnet.infura.io --blocks-output blocks.csv --transactions-output transactions.csv
```

Export ERC20 and ERC721 transfers ([Schema](#token_transferscsv), [Reference](#export_token_transferspy)):

```bash
> python export_token_transfers.py --start-block 0 --end-block 500000 \
--provider-uri file://$HOME/Library/Ethereum/geth.ipc --output token_transfers.csv
```

Export receipts and logs ([Schema](#receiptscsv), [Reference](#export_receipts_and_logspy)):

```bash
> python export_receipts_and_logs.py --transaction-hashes transaction_hashes.txt \
--provider-uri https://mainnet.infura.io --receipts-output receipts.csv --logs-output logs.csv
```

Export ERC20 and ERC721 token details ([Schema](#tokenscsv), [Reference](#export_tokenspy)):

```bash
> python export_tokens.py --token-addresses token_addresses.csv \
--provider-uri https://mainnet.infura.io --output tokens.csv
```

[LIMITATIONS](#limitations)

## Table of Contents

- [Schema](#schema)
  - [blocks.csv](#blockscsv)
  - [transactions.csv](#transactionscsv)
  - [token_transfers.csv](#token_transferscsv)
  - [receipts.csv](#receiptscsv)
  - [logs.csv](#logscsv)
  - [contracts.csv](#contractscsv)
  - [tokens.csv](#tokenscsv)
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
number            | bigint             |
hash              | hex_string         |
parent_hash       | hex_string         |
nonce             | hex_string         |
sha3_uncles       | hex_string         |
logs_bloom        | hex_string         |
transactions_root | hex_string         |
state_root        | hex_string         |
receipts_root     | hex_string         |
miner             | address            |
difficulty        | numeric            |
total_difficulty  | numeric            |
size              | bigint             |
extra_data        | hex_string         |
gas_limit         | bigint             |
gas_used          | bigint             |
timestamp         | bigint             |
transaction_count | bigint             |

### transactions.csv

Column              |    Type     |
--------------------|-------------|
hash             | hex_string  |
nonce            | bigint      |
block_hash       | hex_string  |
block_number     | bigint      |
transaction_index| bigint      |
from_address     | address     |
to_address       | address     |
value            | numeric     |
gas              | bigint      |
gas_price        | bigint      |
input            | hex_string  |

### token_transfers.csv

Column              |    Type     |
--------------------|-------------|
token_address       | address     |
from_address        | address     |
to_address          | address     |
value               | numeric     |
transaction_hash    | hex_string  |
log_index           | bigint      |
block_number        | bigint      |

### receipts.csv

Column                       |    Type     |
-----------------------------|-------------|
transaction_hash             | hex_string  |
transaction_index            | bigint      |
block_hash                   | hex_string  |
block_number                 | bigint      |
cumulative_gas_used          | bigint      |
gas_used                     | bigint      |
contract_address             | address     |
root                         | hex_string  |
status                       | bigint      |

### logs.csv

Column                       |    Type     |
-----------------------------|-------------|
log_index                    | bigint      |
transaction_hash         | hex_string  |
transaction_index        | bigint      |
block_hash               | hex_string  |
block_number             | bigint      |
address                  | address     |
data                     | hex_string  |
topics                   | string      |

### contracts.csv

Column                       |    Type     |
-----------------------------|-------------|
address                      | address     |
bytecode                     | hex_string  |
function_sighashes           | string      |
is_erc20                     | boolean     |
is_erc721                    | boolean     |

### tokens.csv

Column                       |    Type     |
-----------------------------|-------------|
address                      | address     |
symbol                       | string      |
name                         | string      |
decimals                     | bigint      |
total_supply                 | numeric     |

You can find column descriptions in [https://github.com/medvedev1088/ethereum-etl-airflow](https://github.com/medvedev1088/ethereum-etl-airflow/tree/master/dags/resources/stages/raw/schemas)

Note: for the `address` type all hex characters are lower-cased.
`boolean` type can have 2 values: `True` or `False`.

## LIMITATIONS

- `contracts.csv` and `tokens.csv` files don’t include contracts created by message calls (a.k.a. internal transactions).
We are working on adding support for those.
- In case the contract is a proxy, which forwards all calls to a delegate, interface detection doesn’t work,
which means `is_erc20` and `is_erc721` will always be false for proxy contracts.
- The metadata methods (`symbol`, `name`, `decimals`, `total_supply`) for ERC20 are optional, so around 10% of the
contracts are missing this data. Also some contracts (EOS) implement these methods but with wrong return type,
so the metadata columns are missing in this case as well.
- `token_transfers.value`, `tokens.decimals` and `tokens.total_supply` have type `STRING` in BigQuery tables,
because numeric types there can't handle 32-byte integers. You should use
`cast(value as FLOAT64)` (possible loss of precision) or
`safe_cast(value as NUMERIC)` (possible overflow) to convert to numbers.
- The contracts that don't implement `decimals()` function but have the
[fallback function](https://solidity.readthedocs.io/en/v0.4.21/contracts.html#fallback-function) that returns a `boolean`
will have `0` or `1` in the `decimals` column in the CSVs.



## Exporting the Blockchain

1. Install python 3.6 https://www.python.org/downloads/ (3.5 and 3.7 are not supported by this tool for now)

1. You can use Infura if you don't need ERC20 transfers (Infura doesn't support eth_getFilterLogs JSON RPC method).
For that use `-p https://mainnet.infura.io` option for the commands below. If you need ERC20 transfers or want to
export the data ~40 times faster, you will need to set up a local Ethereum node:

1. Install geth https://github.com/ethereum/go-ethereum/wiki/Installing-Geth

1. Start geth.
Make sure it downloaded the blocks that you need by executing `eth.syncing` in the JS console.
You can export blocks below `currentBlock`,
there is no need to wait until the full sync as the state is not needed (unless you also need contracts bytecode
and token details; for those you need to wait until the full sync).

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
    output/token_transfers/start_block=00000000/end_block=00099999/token_transfers_00000000_00099999.csv
    ...
    ```

Should work with geth and parity, on Linux, Mac, Windows.
If you use Parity you should disable warp mode with `--no-warp` option because warp mode
does not place all of the block or receipt data into the database https://wiki.parity.io/Getting-Synced
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

#### Running in Docker

1. Install Docker https://docs.docker.com/install/

1. Build a docker image
    ```bash
    > docker build -t ethereum-etl:latest .
    > docker image ls
    ```

1. Run a container out of the image
    ```bash
    > docker run -v $HOME/output:/ethereum-etl/output ethereum-etl:latest -s 0 -e 5499999 -b 100000 -p https://mainnet.infura.io
    > docker run -v $HOME/output:/ethereum-etl/output ethereum-etl:latest -s 2018-01-01 -e 2018-01-01 -b 100000 -p https://mainnet.infura.io
    ```

#### Command Reference

- [export_blocks_and_transactions.py](#export_blocks_and_transactionspy)
- [export_token_transfers.py](#export_token_transferspy)
- [extract_token_transfers.py](#extract_token_transferspy)
- [export_receipts_and_logs.py](#export_receipts_and_logspy)
- [export_contracts.py](#export_contractspy)
- [export_tokens.py](#export_tokenspy)
- [get_block_range_for_date.py](#get_block_range_for_datepy)
- [get_keccak_hash.py](#get_keccak_hashpy)

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

##### export_token_transfers.py

The API used in this command is not supported by Infura, so you will need a local node.
If you want to use Infura for exporting ERC20 transfers refer to [extract_token_transfers.py](#extract_token_transferspy)

```bash
> python export_token_transfers.py --start-block 0 --end-block 500000 \
--provider-uri file://$HOME/Library/Ethereum/geth.ipc --batch-size 100 --output token_transfers.csv
```

Include `--tokens <token1> <token2>` to filter only certain tokens, e.g.

```bash
> python export_token_transfers.py --start-block 0 --end-block 500000 --provider-uri file://$HOME/Library/Ethereum/geth.ipc \
--output token_transfers.csv --tokens 0x86fa049857e0209aa7d9e616f7eb3b3b78ecfdb0 0x06012c8cf97bead5deae237070f9587f8e7a266d
```

You can tune `--batch-size`, `--max-workers` for performance.

##### export_receipts_and_logs.py

First extract transaction hashes from `transactions.csv`
(Exported with [export_blocks_and_transactions.py](#export_blocks_and_transactionspy)):

```bash
> python extract_csv_column.py --input transactions.csv --column transaction_hash --output transaction_hashes.txt
```

Then export receipts and logs:

```bash
> python export_receipts_and_logs.py --transaction-hashes transaction_hashes.txt \
--provider-uri file://$HOME/Library/Ethereum/geth.ipc --receipts-output receipts.csv --logs-output logs.csv
```

Omit `--receipts-output` or `--logs-output` options if you want to export only logs/receipts.

You can tune `--batch-size`, `--max-workers` for performance.

Upvote this feature request https://github.com/paritytech/parity/issues/9075,
it will make receipts and logs export much faster.

##### extract_token_transfers.py

First export receipt logs with [export_receipts_and_logs.py](#export_receipts_and_logspy).

Then extract transfers from the logs.csv file:

```bash
> python extract_token_transfers.py --logs logs.csv --output token_transfers.csv
```

You can tune `--batch-size`, `--max-workers` for performance.

##### export_contracts.py

First extract contract addresses from `receipts.csv`
(Exported with [export_receipts_and_logs.py](#export_receipts_and_logspy)):

```bash
> python extract_csv_column.py --input receipts.csv --column contract_address --output contract_addresses.txt
```

Then export contracts:

```bash
> python export_contracts.py --contract-addresses contract_addresses.txt \
--provider-uri file://$HOME/Library/Ethereum/geth.ipc --output contracts.csv
```

You can tune `--batch-size`, `--max-workers` for performance.

##### export_tokens.py

First extract token addresses from `contracts.json`
(Exported with [export_contracts.py](#export_contractspy)):

```bash
> python filter_items.py -i contracts.json -p "item['is_erc20'] or item['is_erc721']" | \
python extract_field.py -f address -o token_addresses.txt
```

Then export ERC20 / ERC721 tokens:

```bash
> python export_tokens.py --token-addresses token_addresses.txt \
--provider-uri file://$HOME/Library/Ethereum/geth.ipc --output tokens.csv
```

You can tune `--max-workers` for performance.

##### get_block_range_for_date.py

```bash
> python get_block_range_for_date.py --provider-uri=https://mainnet.infura.io --date 2018-01-01
4832686,4838611
```

##### get_keccak_hash.py

```bash
> python get_keccak_hash.py -i "transfer(address,uint256)"
0xa9059cbb2ab09eb219583f4a59a5d0623ade346d962bcd4e46b11da047c9049b
```

#### Running Tests

```bash
> export ETHEREUM_ETL_RUN_SLOW_TESTS=True
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
  - token_transfers: [schemas/aws/token_transfers.sql](schemas/aws/token_transfers.sql)
  - contracts: [schemas/aws/contracts.sql](schemas/aws/contracts.sql)
  - receipts: [schemas/aws/receipts.sql](schemas/aws/receipts.sql)
  - logs: [schemas/aws/logs.sql](schemas/aws/logs.sql)
  - tokens: [schemas/aws/tokens.sql](schemas/aws/tokens.sql)

### Tables for Parquet Files

Read this article on how to convert CSVs to Parquet https://medium.com/@medvedev1088/converting-ethereum-etl-files-to-parquet-399e048ddd30

- Create the tables:
  - parquet_blocks: [schemas/aws/parquet/parquet_blocks.sql](schemas/aws/parquet/parquet_blocks.sql)
  - parquet_transactions: [schemas/aws/parquet/parquet_transactions.sql](schemas/aws/parquet/parquet_transactions.sql)
  - parquet_token_transfers: [schemas/aws/parquet/parquet_token_transfers.sql](schemas/aws/parquet/parquet_token_transfers.sql)

Note that DECIMAL type is limited to 38 digits in Hive https://cwiki.apache.org/confluence/display/Hive/LanguageManual+Types#LanguageManualTypes-decimal
so values greater than 38 decimals will be null.

## Querying in Google BigQuery

Refer to https://github.com/medvedev1088/ethereum-etl-airflow for the instructions.

### Public Dataset

You can query the data that's updated daily in the public BigQuery dataset
https://medium.com/@medvedev1088/ethereum-blockchain-on-google-bigquery-283fb300f579
