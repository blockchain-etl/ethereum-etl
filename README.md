# Ethereum ETL

[![Build Status](https://travis-ci.org/blockchain-etl/ethereum-etl.png)](https://travis-ci.org/blockchain-etl/ethereum-etl)
[![Join the chat at https://gitter.im/ethereum-eth](https://badges.gitter.im/ethereum-etl.svg)](https://gitter.im/ethereum-etl/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Telegram](https://img.shields.io/badge/telegram-join%20chat-blue.svg)](https://t.me/joinchat/GsMpbA3mv1OJ6YMp3T5ORQ)
[![Discord](https://img.shields.io/badge/discord-join%20chat-blue.svg)](https://discord.gg/wukrezR)

Ethereum ETL lets you convert blockchain data into convenient formats like CSVs and relational databases.

*Do you just want to query Ethereum data right away? Use the [public dataset in BigQuery](https://console.cloud.google.com/marketplace/details/ethereum/crypto-ethereum-blockchain).*

[Full documentation available here](http://ethereum-etl.readthedocs.io/).

## Quickstart

Install Ethereum ETL:

```bash
pip3 install ethereum-etl
```

Export blocks and transactions ([Schema](docs/schema.md#blockscsv), [Reference](docs/commands.md#export_blocks_and_transactions)):

```bash
> ethereumetl export_blocks_and_transactions --start-block 0 --end-block 500000 \
--blocks-output blocks.csv --transactions-output transactions.csv \
--provider-uri https://mainnet.infura.io/v3/7aef3f0cd1f64408b163814b22cc643c
```

Export ERC20 and ERC721 transfers ([Schema](docs/schema.md#token_transferscsv), [Reference](docs/commands.md##export_token_transfers)):

```bash
> ethereumetl export_token_transfers --start-block 0 --end-block 500000 \
--provider-uri file://$HOME/Library/Ethereum/geth.ipc --output token_transfers.csv
```

Export traces ([Schema](docs/schema.md#tracescsv), [Reference](docs/commands.md#export_traces)):

```bash
> ethereumetl export_traces --start-block 0 --end-block 500000 \
--provider-uri file://$HOME/Library/Ethereum/parity.ipc --output traces.csv
```

---

Stream blocks, transactions, logs, token_transfers continually to console ([Reference](docs/commands.md#stream)):

```bash
> pip3 install ethereum-etl[streaming]
> ethereumetl stream --start-block 500000 -e block,transaction,log,token_transfer --log-file log.txt \
--provider-uri https://mainnet.infura.io/v3/7aef3f0cd1f64408b163814b22cc643c
```

Find other commands [here](https://ethereum-etl.readthedocs.io/en/latest/commands/).

For the latest version, check out the repo and call 
```bash
> pip3 install -e . 
> python3 ethereumetl.py
```

## Useful Links

- [Schema](https://ethereum-etl.readthedocs.io/en/latest/schema/)
- [Command Reference](https://ethereum-etl.readthedocs.io/en/latest/commands/)
- [Documentation](https://ethereum-etl.readthedocs.io/)
- [Exporting the Blockchain](https://ethereum-etl.readthedocs.io/en/latest/exporting-the-blockchain/)
- [Querying in Amazon Athena](https://ethereum-etl.readthedocs.io/en/latest/amazon-athena/)
- [Querying in Google BigQuery](https://ethereum-etl.readthedocs.io/en/latest/google-bigquery/)
- [Querying in Kaggle](https://www.kaggle.com/bigquery/ethereum-blockchain)
- [Airflow DAGs](https://github.com/blockchain-etl/ethereum-etl-airflow)
- [Postgres ETL](https://github.com/blockchain-etl/ethereum-etl-postgresql)
- [Ethereum 2.0 ETL](https://github.com/blockchain-etl/ethereum2-etl)

## Running Tests

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

## Running in Docker

1. Install Docker: https://docs.docker.com/install/

2. Build a docker image
        
        > docker build -t ethereum-etl:latest .
        > docker image ls
        
3. Run a container out of the image

        > docker run -v $HOME/output:/ethereum-etl/output ethereum-etl:latest export_all -s 0 -e 5499999 -b 100000 -p https://mainnet.infura.io
        > docker run -v $HOME/output:/ethereum-etl/output ethereum-etl:latest export_all -s 2018-01-01 -e 2018-01-01 -p https://mainnet.infura.io

4. Run streaming to console or Pub/Sub

        > docker build -t ethereum-etl:latest -f Dockerfile .
        > echo "Stream to console"
        > docker run ethereum-etl:latest stream --start-block 500000 --log-file log.txt
        > echo "Stream to Pub/Sub"
        > docker run -v /path_to_credentials_file/:/ethereum-etl/ --env GOOGLE_APPLICATION_CREDENTIALS=/ethereum-etl/credentials_file.json ethereum-etl:latest stream --start-block 500000 --output projects/<your-project>/topics/crypto_ethereum

## Projects using Ethereum ETL
* [Google](https://goo.gl/oY5BCQ) - Public BigQuery Ethereum datasets
* [Nansen](https://www.nansen.ai/?ref=ethereumetl) - Analytics platform for Ethereum
