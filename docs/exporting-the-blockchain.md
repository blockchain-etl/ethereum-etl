## Exporting the Blockchain

If you'd like to have blockchain data set up and hosted for you, [get in touch with us at D5](https://d5.ai/?ref=ethereumetl).

1. Install python 3.5.3+ https://www.python.org/downloads/

1. You can use Infura if you don't need ERC20 transfers (Infura doesn't support eth_getFilterLogs JSON RPC method).
For that use `-p https://mainnet.infura.io` option for the commands below. If you need ERC20 transfers or want to
export the data ~40 times faster, you will need to set up a local Ethereum node:

1. Install geth https://github.com/ethereum/go-ethereum/wiki/Installing-Geth

1. Start geth.
Make sure it downloaded the blocks that you need by executing `eth.syncing` in the JS console.
You can export blocks below `currentBlock`,
there is no need to wait until the full sync as the state is not needed (unless you also need contracts bytecode
and token details; for those you need to wait until the full sync).

1. Install Ethereum ETL: `> pip3 install ethereum-etl`

1. Export all:

```bash
> ethereumetl export_all --help
> ethereumetl export_all -s 0 -e 5999999 -b 100000 -p file://$HOME/Library/Ethereum/geth.ipc -o output
```
    
In case `ethereumetl` command is not available in PATH, use `python3 -m ethereumetl` instead.

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

If you see weird behavior, e.g. wrong number of rows in the CSV files or corrupted files,
check out this issue: https://github.com/medvedev1088/ethereum-etl/issues/28

### Export in 2 Hours

You can use AWS Auto Scaling and Data Pipeline to reduce the exporting time to a few hours.
Read [this article](https://medium.com/@medvedev1088/how-to-export-the-entire-ethereum-blockchain-to-csv-in-2-hours-for-10-69fef511e9a2) for details.

### Running in Docker

1. Install Docker https://docs.docker.com/install/

2. Build a docker image
        
        > docker build -t ethereum-etl:latest .
        > docker image ls
        
    
3. Run a container out of the image

        > docker run -v $HOME/output:/ethereum-etl/output ethereum-etl:latest export_all -s 0 -e 5499999 -b 100000 -p https://mainnet.infura.io
        > docker run -v $HOME/output:/ethereum-etl/output ethereum-etl:latest export_all -s 2018-01-01 -e 2018-01-01 -p https://mainnet.infura.io

1. Run streaming to console or Pub/Sub

        > docker build -t ethereum-etl:latest-streaming -f Dockerfile_with_streaming .
        > echo "Stream to console"
        > docker run ethereum-etl:latest-streaming stream --start-block 500000 --log-file log.txt
        > echo "Stream to Pub/Sub"
        > docker run -v /path_to_credentials_file/:/ethereum-etl/ --env GOOGLE_APPLICATION_CREDENTIALS=/ethereum-etl/credentials_file.json ethereum-etl:latest-streaming stream --start-block 500000 --output projects/<your-project>/topics/crypto_ethereum

### Running Tests

```bash
> pip3 install -e .[dev,streaming]
> export ETHEREUM_ETL_RUN_SLOW_TESTS=True
> pytest -vv
```

### Running Tox Tests

```bash
> pip3 install tox
> tox
```
