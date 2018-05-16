# Ethereum ETL

One-liner for blocks:

```bash
> python gen_blocks_rpc.py --end-block=1000 | \
python exchange_with_ipc.py --ipc-path=$HOME/Library/Ethereum/geth.ipc | \
python extract_blocks.py > blocks.csv
```

One-liner for transactions:

```bash
> python gen_blocks_rpc.py --end-block=1000 | \
python exchange_with_ipc.py --ipc-path=$HOME/Library/Ethereum/geth.ipc | \
python extract_transactions.py > transactions.csv
```

One-liner for ERC20 transfers:

```bash
> python export_erc20_transfers.py --start-block=0 --end-block=500000 --ipc-path=$HOME/Library/Ethereum/geth.ipc > erc20_transfers.csv
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

Parity is not supported for now https://github.com/medvedev1088/ethereum-etl/issues/2

Start geth. 
Make sure it downloaded the blocks that you need by executing `eth.synching` in the JS console.
You can export blocks below `currentBlock`, 
there is no need to wait until the full sync as the state is not needed.

Install all dependencies:

```bash
> pip install -r requirements.txt
```

Run in the terminal:

```bash
> ./export_all.sh -h
Usage: ./export_all.sh [-s <start_block>] [-e <end_block>] [-b <batch_size>] [-i <ipc_path>] [-o <output_dir>]
> ./export_all.sh -s 0 -e 5499999 -b 100000 -i ~/Library/Ethereum/geth.ipc -o output 
```

#### Commands
Generate JSON RPC calls for exporting blocks and transactions for specified block range:

```bash
> python gen_blocks_rpc.py --start-block=0 --end-block=1000 --output=blocks_rpc.json
```

Call JSON RPC via IPC for exporting blocks and transactions:

```bash
> python exchange_with_ipc.py --ipc-path=$HOME/Library/Ethereum/geth.ipc --input=blocks_rpc.json --output=blocks_rpc_output.json
```

Extract blocks from JSON RPC response:

```bash
> python extract_blocks.py --input blocks_rpc_output.json --output blocks.csv
```

Extract transactions from JSON RPC response:

```bash
> python extract_transactions.py --input blocks_rpc_output.json --output transactions.csv
```

Export ERC20 transfers:

```bash
> python export_erc20_transfers.py --start-block=0 --end-block=500000 --ipc-path=$HOME/Library/Ethereum/geth.ipc --batch-size=100 > erc20_transfers.csv
```
 
Tested with Python 3.6, geth 1.8.7, Ubuntu 16.04.4

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
1. Send batch requests http://www.jsonrpc.org/specification#batch. 
1. Support Parity
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