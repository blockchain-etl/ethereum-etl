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
`currentBlock` is what you need to check. 
You don't need to wait until the full sync as state is not needed.

Install all dependencies:

```
> pip install typing future argparse six
```

Generate JSON RPC calls for exporting blocks and transactions for specified block range:

```
> python gen_blocks_rpc.py --start-block=0 --end-block=1000 --output=blocks_rpc.json
```

Call JSON RPC via IPC for exporting blocks and transactions:

```
> nc -U ~/Library/Ethereum/geth.ipc < blocks_rpc.json > blocks_rpc_output.json
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
> nc -U ~/Library/Ethereum/geth.ipc --input=transaction_receipts_rpc.json --output=transaction_receipts_rpc_output.json
```

Extract ERC20 transfers from transaction receipts:

```
> python extract_erc20_transfers.py --input transaction_receipts_rpc_output.json --output erc20_transfers.csv
```

Should work with python 2 and 3. Tested with Python 3.6.



