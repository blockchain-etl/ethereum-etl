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
--provider-uri https://mainnet.infura.io --blocks-output blocks.csv --transactions-output transactions.csv
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
> ethereumetl stream --start-block 500000 -e block,transaction,log,token_transfer --log-file log.txt
```

Find other commands [here](http://ethereum-etl.readthedocs.io/commands).

For the latest version, check out the repo and call 
```bash
> pip3 install -e . 
> python3 ethereumetl.py
```

### Useful Links

- [Schema](http://ethereum-etl.readthedocs.io/schema)
- [Command Reference](http://ethereum-etl.readthedocs.io/commands)
- [Tests](http://ethereum-etl.readthedocs.io/tests)
- [Exporting the Blockchain](http://ethereum-etl.readthedocs.io/exporting-the-blockchain)
- [Running in Docker](http://ethereum-etl.readthedocs.io/docker)
- [Querying in Amazon Athena](http://ethereum-etl.readthedocs.io/amazon-athena)
- [Querying in Google BigQuery](http://ethereum-etl.readthedocs.io/google-bigquery)
- [Airflow DAGs](https://github.com/blockchain-etl/ethereum-etl-airflow)
- [Postgres ETL](https://github.com/blockchain-etl/ethereum-etl-postgresql)