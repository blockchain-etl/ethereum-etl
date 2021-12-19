# Commands

All the commands accept `-h` parameter for help, e.g.:

```bash
> ethereumetl export_blocks_and_transactions -h

Usage: ethereumetl export_blocks_and_transactions [OPTIONS]

  Export blocks and transactions.

Options:
  -s, --start-block INTEGER   Start block
  -e, --end-block INTEGER     End block  [required]
  -b, --batch-size INTEGER    The number of blocks to export at a time.
  -p, --provider-uri TEXT     The URI of the web3 provider e.g.
                              file://$HOME/Library/Ethereum/geth.ipc or
                              https://mainnet.infura.io
  -w, --max-workers INTEGER   The maximum number of workers.
  --blocks-output TEXT        The output file for blocks. If not provided
                              blocks will not be exported. Use "-" for stdout
  --transactions-output TEXT  The output file for transactions. If not
                              provided transactions will not be exported. Use
                              "-" for stdout
  -h, --help                  Show this message and exit.
```

For the `--output` parameters the supported types are csv and json. The format type is inferred from the output file name.

#### export_blocks_and_transactions

```bash
> ethereumetl export_blocks_and_transactions --start-block 0 --end-block 500000 \
--provider-uri file://$HOME/Library/Ethereum/geth.ipc \
--blocks-output blocks.csv --transactions-output transactions.csv
```

Omit `--blocks-output` or `--transactions-output` options if you want to export only transactions/blocks.

You can tune `--batch-size`, `--max-workers` for performance.

[Blocks and transactions schema](schema.md#blockscsv).

#### export_token_transfers

The API used in this command is not supported by Infura, so you will need a local node.
If you want to use Infura for exporting ERC20 transfers refer to [extract_token_transfers](#extract_token_transfers)

```bash
> ethereumetl export_token_transfers --start-block 0 --end-block 500000 \
--provider-uri file://$HOME/Library/Ethereum/geth.ipc --batch-size 100 --output token_transfers.csv
```

Include `--tokens <token1> --tokens <token2>` to filter only certain tokens, e.g.

```bash
> ethereumetl export_token_transfers --start-block 0 --end-block 500000 \
--provider-uri file://$HOME/Library/Ethereum/geth.ipc --output token_transfers.csv \
--tokens 0x86fa049857e0209aa7d9e616f7eb3b3b78ecfdb0 --tokens 0x06012c8cf97bead5deae237070f9587f8e7a266d
```

You can tune `--batch-size`, `--max-workers` for performance.

[Token transfers schema](schema.md#token_transferscsv).

#### export_receipts_and_logs

First extract transaction hashes from `transactions.csv`
(Exported with [export_blocks_and_transactions](#export_blocks_and_transactions)):

```bash
> ethereumetl extract_csv_column --input transactions.csv --column hash --output transaction_hashes.txt
```

Then export receipts and logs:

```bash
> ethereumetl export_receipts_and_logs --transaction-hashes transaction_hashes.txt \
--provider-uri file://$HOME/Library/Ethereum/geth.ipc --receipts-output receipts.csv --logs-output logs.csv
```

Omit `--receipts-output` or `--logs-output` options if you want to export only logs/receipts.

You can tune `--batch-size`, `--max-workers` for performance.

Upvote this feature request https://github.com/paritytech/parity/issues/9075,
it will make receipts and logs export much faster.

[Receipts and logs schema](schema.md#receiptscsv).

#### extract_token_transfers

First export receipt logs with [export_receipts_and_logs](#export_receipts_and_logs).

Then extract transfers from the logs.csv file:

```bash
> ethereumetl extract_token_transfers --logs logs.csv --output token_transfers.csv
```

You can tune `--batch-size`, `--max-workers` for performance.

[Token transfers schema](schema.md#token_transferscsv).

#### export_contracts

First extract contract addresses from `receipts.csv`
(Exported with [export_receipts_and_logs](#export_receipts_and_logs)):

```bash
> ethereumetl extract_csv_column --input receipts.csv --column contract_address --output contract_addresses.txt
```

Then export contracts:

```bash
> ethereumetl export_contracts --contract-addresses contract_addresses.txt \
--provider-uri file://$HOME/Library/Ethereum/geth.ipc --output contracts.csv
```

You can tune `--batch-size`, `--max-workers` for performance.

[Contracts schema](schema.md#contractscsv).

#### export_tokens

First extract token addresses from `contracts.json`
(Exported with [export_contracts](#export_contracts)):

```bash
> ethereumetl filter_items -i contracts.json -p "item['is_erc20'] or item['is_erc721']" | \
ethereumetl extract_field -f address -o token_addresses.txt
```

Then export ERC20 / ERC721 tokens:

```bash
> ethereumetl export_tokens --token-addresses token_addresses.txt \
--provider-uri file://$HOME/Library/Ethereum/geth.ipc --output tokens.csv
```

You can tune `--max-workers` for performance.

[Tokens schema](schema.md#tokenscsv).

#### export_traces

Also called internal transactions.
The API used in this command is not supported by Infura, 
so you will need a local Parity archive node (`parity --tracing on`). 
Make sure your node has at least 8GB of memory, or else you will face timeout errors. 
See [this issue](https://github.com/blockchain-etl/ethereum-etl/issues/137) 

```bash
> ethereumetl export_traces --start-block 0 --end-block 500000 \
--provider-uri file://$HOME/Library/Ethereum/parity.ipc --batch-size 100 --output traces.csv
```

You can tune `--batch-size`, `--max-workers` for performance.

[Traces schema](schema.md#tracescsv).

#### export_geth_traces

Read [Differences between geth and parity traces.csv](schema.md#differences-between-geth-and-parity-tracescsv)

The API used in this command is not supported by Infura, 
so you will need a local Geth archive node (`geth --gcmode archive --syncmode full --ipcapi debug`).
When using rpc, add `--rpc --rpcapi debug` options.

```bash
> ethereumetl export_geth_traces --start-block 0 --end-block 500000 \
--provider-uri file://$HOME/Library/Ethereum/geth.ipc --batch-size 100 --output geth_traces.json
```

You can tune `--batch-size`, `--max-workers` for performance.

#### extract_geth_traces

```bash
> ethereumetl extract_geth_traces --input geth_traces.json --output traces.csv
```

You can tune `--batch-size`, `--max-workers` for performance.

#### get_block_range_for_date

```bash
> ethereumetl get_block_range_for_date --provider-uri=https://mainnet.infura.io/v3/7aef3f0cd1f64408b163814b22cc643c --date 2018-01-01
4832686,4838611
```

#### get_keccak_hash

```bash
> ethereumetl get_keccak_hash -i "transfer(address,uint256)"
0xa9059cbb2ab09eb219583f4a59a5d0623ade346d962bcd4e46b11da047c9049b
```

#### stream

```bash
> pip3 install ethereum-etl[streaming]
> ethereumetl stream --provider-uri https://mainnet.infura.io/v3/7aef3f0cd1f64408b163814b22cc643c --start-block 500000
```

- This command outputs blocks, transactions, logs, token_transfers to the console by default.
- Entity types can be specified with the `-e` option, 
e.g. `-e block,transaction,log,token_transfer,trace,contract,token`.
- Use `--output` option to specify the Google Pub/Sub topic, Postgres database or GCS bucket where to publish blockchain data, 
    - For Google PubSub: `--output=projects/<your-project>/topics/crypto_ethereum`. 
    Data will be pushed to `projects/<your-project>/topics/crypto_ethereum.blocks`, `projects/<your-project>/topics/crypto_ethereum.transactions` etc. topics.
    - For Postgres: `--output=postgresql+pg8000://<user>:<password>@<host>:<port>/<database_name>`, 
    e.g. `--output=postgresql+pg8000://postgres:admin@127.0.0.1:5432/ethereum`.
    - For GCS:  `--output=gs://<bucket_name>`. Make sure to install and initialize `gcloud` cli.
    - Those output types can be combined with a comma e.g. `--output=gs://<bucket_name>,projects/<your-project>/topics/crypto_ethereum`
    The [schema](https://github.com/blockchain-etl/ethereum-etl-postgres/tree/master/schema) 
    and [indexes](https://github.com/blockchain-etl/ethereum-etl-postgres/tree/master/indexes) can be found in this 
    repo [ethereum-etl-postgres](https://github.com/blockchain-etl/ethereum-etl-postgres). 
- The command saves its state to `last_synced_block.txt` file where the last synced block number is saved periodically.
- Specify either `--start-block` or `--last-synced-block-file` option. `--last-synced-block-file` should point to the 
file where the block number, from which to start streaming the blockchain data, is saved.
- Use the `--lag` option to specify how many blocks to lag behind the head of the blockchain. It's the simplest way to 
handle chain reorganizations - they are less likely the further a block from the head.
- You can tune `--period-seconds`, `--batch-size`, `--block-batch-size`, `--max-workers` for performance.
- Refer to [blockchain-etl-streaming](https://github.com/blockchain-etl/blockchain-etl-streaming) for
instructions on deploying it to Kubernetes. 

Stream blockchain data continually to Google Pub/Sub:

```bash
> export GOOGLE_APPLICATION_CREDENTIALS=/path_to_credentials_file.json
> ethereumetl stream --start-block 500000 --output projects/<your-project>/topics/crypto_ethereum
```

Stream blockchain data to a Postgres database:

```bash
ethereumetl stream --start-block 500000 --output postgresql+pg8000://<user>:<password>@<host>:5432/<database>
```

The [schema](https://github.com/blockchain-etl/ethereum-etl-postgres/tree/master/schema) 
and [indexes](https://github.com/blockchain-etl/ethereum-etl-postgres/tree/master/indexes) can be found in this 
repo [ethereum-etl-postgres](https://github.com/blockchain-etl/ethereum-etl-postgres).