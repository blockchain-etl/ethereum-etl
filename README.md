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
python extract_transactions.py | python extract_column_from_csv.py --column=tx_hash | \
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

Start geth, make sure it's synchronized with the Ethereum network.

Run in the terminal:

```
> pip install typing future argparse six
> python gen_blocks_rpc.py --start-block=0 --end-block=1000 --output=blocks_rpc.json
> nc -U ~/Library/Ethereum/geth.ipc < blocks_rpc.json > blocks_rpc_output.json
> python extract_blocks.py --input blocks_rpc_output.json --output blocks.csv
> python extract_transactions.py --input blocks_rpc_output.json --output transactions.csv

> python extract_column_from_csv.py --column=tx_hash --input=transactions.csv --output transaction_hashes.csv
> python gen_transaction_receipts_rpc.py --input=transaction_hashes.csv --output transaction_receipts_rpc.json
> nc -U ~/Library/Ethereum/geth.ipc --input=transaction_receipts_rpc.json --output=transaction_receipts_rpc_output.json
> python extract_erc20_transfers.py --input transaction_receipts_rpc_output.json --output erc20_transfers.csv
```

Should work on both python 2 and 3. Tested on python2.7.

