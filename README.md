# Ethereum ETL

One-liner for blocks and transactions:

```bash
> python export_blocks_and_transactions.py --start-block=0 --end-block=500000 \
--ipc-path=$HOME/Library/Ethereum/geth.ipc --blocks-output=blocks.csv --transactions-output=transactions.csv
```

One-liner for blocks:

```bash
> python export_blocks_and_transactions.py --start-block=0 --end-block=500000 \
--ipc-path=$HOME/Library/Ethereum/geth.ipc --blocks-output=blocks.csv
```

One-liner for ERC20 transfers:

```bash
> python export_erc20_transfers.py --start-block=0 --end-block=500000 --ipc-path=$HOME/Library/Ethereum/geth.ipc \
--output=erc20_transfers.csv
```

One-liner for ERC20 transfers, filtered for list of tokens:

```bash
> python export_erc20_transfers.py --start-block=0 --end-block=500000 --ipc-path=$HOME/Library/Ethereum/geth.ipc \
--output=erc20_transfers.csv --tokens=0x86fa049857e0209aa7d9e616f7eb3b3b78ecfdb0,0x06012c8cf97bead5deae237070f9587f8e7a266d
```

Read this article https://medium.com/@medvedev1088/exporting-and-analyzing-ethereum-blockchain-f5353414a94e

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
block_miner             | hex_string         |
block_difficulty        | bigint             |
block_total_difficulty  | bigint             |
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
tx_from             | hex_string  |
tx_to               | hex_string  |
tx_value            | bigint      |
tx_gas              | bigint      |
tx_gas_price        | bigint      |
tx_input            | hex_string  |

`erc20_transfers.csv`

Column              |    Type     |
--------------------|--------------
erc20_token         | hex_string  |
erc20_from          | hex_string  |
erc20_to            | hex_string  |
erc20_value         | bigint      |
erc20_tx_hash       | hex_string  |
erc20_block_number  | bigint      |

### Usage

If you want to export just a few thousand blocks and don't want to sync your own node 
refer to https://github.com/medvedev1088/ethereum-scraper.

1. Install python 3.6 https://conda.io/miniconda.html

1. Install geth https://github.com/ethereum/go-ethereum/wiki/Installing-Geth

1. Start geth. 
Make sure it downloaded the blocks that you need by executing `eth.synching` in the JS console.
You can export blocks below `currentBlock`, 
there is no need to wait until the full sync as the state is not needed.

1. Install all dependencies:

    ```bash
    > pip install -r requirements.txt
    ```

1. Run in the terminal:

    ```bash
    > ./export_all.sh -h
    Usage: ./export_all.sh -s <start_block> -e <end_block> -b <batch_size> -i <ipc_path> [-o <output_dir>]
    > ./export_all.sh -s 0 -e 5499999 -b 100000 -i ~/Library/Ethereum/geth.ipc -o output 
    ```

Should work with geth and parity, on Linux, Mac, Windows. 
Tested with Python 3.6, geth 1.8.7, Ubuntu 16.04.4

#### Windows

Additional steps:

1. Install Visual C++ Build Tools https://landinghub.visualstudio.com/visual-cpp-build-tools

1. Install Git Bash with  Git for Windows https://git-scm.com/download/win

1. Run in Git Bash:

    ```bash
    >  ./export_all.sh -s 0 -e 999999 -b 100000 -i '\\.\pipe\geth.ipc' -o output 
    ```

#### Commands

- Export blocks and transactions:

```bash
> python export_blocks_and_transactions.py --start-block=0 --end-block=500000 \
--ipc-path=$HOME/Library/Ethereum/geth.ipc --blocks-output=blocks.csv --transactions-output=transactions.csv
```

Omit `--blocks-output` or `--transactions-output` options if you don't want to export blocks/transactions.

If you run geth on a unix-based OS try using `--strategy=unix-geth`, it will work around 2 times faster 
due to the way IPC interaction is handled.

- Export ERC20 transfers:

```bash
> python export_erc20_transfers.py --start-block=0 --end-block=500000 \
--ipc-path=$HOME/Library/Ethereum/geth.ipc --batch-size=100 --output=erc20_transfers.csv
```

Include `--tokens=<comma_separated_list_of_token_address>` to filter only certain tokens, e.g.

```bash
> python export_erc20_transfers.py --start-block=0 --end-block=500000 --ipc-path=$HOME/Library/Ethereum/geth.ipc \
--output=erc20_transfers.csv --tokens=0x86fa049857e0209aa7d9e616f7eb3b3b78ecfdb0,0x06012c8cf97bead5deae237070f9587f8e7a266d
```

### Running Tests

```bash
> pytest
```

### Uploading to S3

Upload blocks, transactions, erc20_transfers:

```bash
> cd output
> aws s3 sync . s3://<your_bucket>/athena/lab1/blocks --region ap-southeast-1  --exclude "*" --include "*blocks_*.csv"
> aws s3 sync . s3://<your_bucket>/athena/lab1/transactions --region ap-southeast-1  --exclude "*" --include "*transactions_*.csv"
> aws s3 sync . s3://<your_bucket>/athena/lab1/erc20_transfers --region ap-southeast-1  --exclude "*" --include "*erc20_transfers_*.csv"
```

Change `--include` option to

Upload first 1 million blocks: `--include "blocks_00*.csv"`

Upload second 1 million blocks: `--include "blocks_01*.csv"`

Upload transactions for first 1 million blocks: `--include "transactions_00*.csv"`

Upload ERC20 transfers for first 1 million blocks: `--include "erc20_transfers_00*.csv"`

### Creating Tables in AWS Athena

Create database:

```sql
CREATE DATABASE lab1;
```

#### blocks

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS blocks (
    block_number BIGINT,
    block_hash STRING,
    block_parent_hash STRING,
    block_nonce STRING,
    block_sha3_uncles STRING,
    block_logs_bloom STRING,
    block_transactions_root STRING,
    block_state_root STRING,
    block_miner STRING,
    block_difficulty BIGINT,
    block_total_difficulty BIGINT,
    block_size BIGINT,
    block_extra_data STRING,
    block_gas_limit BIGINT,
    block_gas_used BIGINT,
    block_timestamp BIGINT,
    block_transaction_count BIGINT
)
PARTITIONED BY (start_block BIGINT, end_block BIGINT)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
    'serialization.format' = ',',
    'field.delim' = ',',
    'escape.delim' = '\\'
)
STORED AS TEXTFILE
LOCATION 's3://<your_bucket>/athena/lab1/blocks'
TBLPROPERTIES (
  'skip.header.line.count' = '1'
);
```

#### transactions

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS transactions (
    tx_hash STRING, 
    tx_nonce BIGINT, 
    tx_block_hash STRING,
    tx_block_number BIGINT, 
    tx_index BIGINT, 
    tx_from STRING, 
    tx_to STRING, 
    tx_value BIGINT, 
    tx_gas BIGINT, 
    tx_gas_price BIGINT, 
    tx_input STRING  
)
PARTITIONED BY (start_block BIGINT, end_block BIGINT)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
    'serialization.format' = ',',
    'field.delim' = ',',
    'escape.delim' = '\\'
)
STORED AS TEXTFILE
LOCATION 's3://<your_bucket>/athena/lab1/transactions'
TBLPROPERTIES (
  'skip.header.line.count' = '1'
);
```

#### erc20_transfers

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS erc20_transfers (
    erc20_token STRING, 
    erc20_from STRING, 
    erc20_to STRING, 
    erc20_value BIGINT, 
    erc20_tx_hash STRING, 
    erc20_block_number BIGINT  
)
PARTITIONED BY (start_block BIGINT, end_block BIGINT)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
    'serialization.format' = ',',
    'field.delim' = ',',
    'escape.delim' = '\\'
)
STORED AS TEXTFILE
LOCATION 's3://<your_bucket>/athena/lab1/erc20_transfers'
TBLPROPERTIES (
  'skip.header.line.count' = '1'
);
```

Add partitions:

```sql
MSCK REPAIR TABLE blocks;
MSCK REPAIR TABLE transactions;
MSCK REPAIR TABLE erc20_transfers;
```

Note that BIGINT is 8-byte signed integer in Hive https://cwiki.apache.org/confluence/display/Hive/LanguageManual+Types#LanguageManualTypes-IntegralTypes(TINYINT,SMALLINT,INT/INTEGER,BIGINT)
so some ERC20 values will be null.

### TODOs

1. Unit tests
1. Add HTTPProvider
1. Error handling and logging

### SQL for Blockchain

I'm currently working on a SaaS solution for analysts and developers:

- Web console for running SQLs based on Redash http://demo.redash.io/
- Built on top of AWS, cost efficient
- Can provide access to raw CSV data if needed
- Support for internal transactions in the future
- Support for API access in the future
- Support for Bitcoin and other blockchains in the future
- Users pay per query

Contact me if you would like to join evge.medvedev@gmail.com