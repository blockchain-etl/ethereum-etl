# Ethereum ETL

One-liner for blocks:

```
> python gen_blocks_rpc.py --end-block=1000 | nc -U ~/Library/Ethereum/geth.ipc | python extract_blocks.py > blocks.csv
```

One-liner for transactions:

```
> python gen_blocks_rpc.py --end-block=1000 | nc -U ~/Library/Ethereum/geth.ipc | python extract_transactions.py > transactions.csv
```

One-liner for ERC20 transfers:

```
> python gen_blocks_rpc.py --end-block=1000 | nc -U ~/Library/Ethereum/geth.ipc | \
python extract_transactions.py | python extract_csv_column.py --column=tx_hash | \
python gen_transaction_receipts_rpc.py | nc -U ~/Library/Ethereum/geth.ipc | \
python extract_erc20_transfers.py > erc20_transfers.csv
```

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

Start geth. 
Make sure it downloaded the blocks that you need by executing `eth.synching` in the JS console.
You can export blocks below `currentBlock`, 
there is no need to wait until the full sync as the state is not needed.

Install all dependencies:

```
> pip install typing future argparse six
```

Run in the terminal:

```
> ./export_all.sh -h
Usage: ./export_all.sh [-s <start_block>] [-e <end_block>] [-b <batch_size>] [-i <ipc_path>] [-o <output_dir>]
> ./export_all.sh -s 0 -e 5499999 -b 100000 -i ~/Library/Ethereum/geth.ipc -o output 
```

#### Commands
Generate JSON RPC calls for exporting blocks and transactions for specified block range:

```
> python gen_blocks_rpc.py --start-block=0 --end-block=1000 --output=blocks_rpc.json
```

Call JSON RPC via IPC for exporting blocks and transactions:

```
> python exchange_with_ipc.py --ipc-path=~/Library/Ethereum/geth.ipc --input=blocks_rpc.json --output=blocks_rpc_output.json
```

Extract blocks from JSON RPC response:

```
> python extract_blocks.py --input blocks_rpc_output.json --output blocks.csv
```

Extract transactions from JSON RPC response:

```
> python extract_transactions.py --input blocks_rpc_output.json --output transactions.csv
```

Extract transaction hashes from transactions.csv:

```
> python extract_csv_column.py --column=tx_hash --input=transactions.csv --output transaction_hashes.csv
```

Generate JSON RPC calls for exporting transaction receipts for given transaction hashes:

```
> python gen_transaction_receipts_rpc.py --input=transaction_hashes.csv --output transaction_receipts_rpc.json
```

Call JSON RPC via IPC for exporting transaction receipts:

```
> python exchange_with_ipc.py --ipc-path=~/Library/Ethereum/geth.ipc --input=transaction_receipts_rpc.json --output=transaction_receipts_rpc_output.json
```

Extract ERC20 transfers from transaction receipts:

```
> python extract_erc20_transfers.py --input transaction_receipts_rpc_output.json --output erc20_transfers.csv
```
 
Tested with Python 3.6, geth 1.8.7, Ubuntu 16.04.4

### Uploading to S3

Upload blocks, transactions, erc20_transfers:

```
> cd output
> aws s3 sync . s3://<your_bucket>/athena/lab1/blocks --region ap-southeast-1  --exclude "*" --include "blocks_*.csv"
> aws s3 sync . s3://<your_bucket>/athena/lab1/transactions --region ap-southeast-1  --exclude "*" --include "transactions_*.csv"
> aws s3 sync . s3://<your_bucket>/athena/lab1/erc20_transfers --region ap-southeast-1  --exclude "*" --include "erc20_transfers_*.csv"
```

Change `--include` option to

Upload first 1 million blocks: `--include "blocks_00*.csv"`

Upload second 1 million blocks: `--include "blocks_01*.csv"`

Upload transactions for first 1 million blocks: `--include "transactions_00*.csv"`

Upload ERC20 transfers for first 1 million blocks: `--include "erc20_transfers_00*.csv"`

### Creating Table in AWS Athena

Create database:

```sql
CREATE DATABASE lab1;
```

Create `blocks` table:

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

Create `transactions` table:

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

Create `erc20_transfers` table:



