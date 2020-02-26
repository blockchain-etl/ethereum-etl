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

Export blocks and transactions:

```bash
> ethereumetl export_blocks_and_transactions --start-block 0 --end-block 500000 \
--provider-uri https://mainnet.infura.io --blocks-output blocks.csv --transactions-output transactions.csv
```

Export ERC20 and ERC721 transfers:

```bash
> ethereumetl export_token_transfers --start-block 0 --end-block 500000 \
--provider-uri file://$HOME/Library/Ethereum/geth.ipc --output token_transfers.csv
```

Export traces:

```bash
> ethereumetl export_traces --start-block 0 --end-block 500000 \
--provider-uri file://$HOME/Library/Ethereum/parity.ipc --output traces.csv
```

---

Stream blocks, transactions, logs, token_transfers continually to console:

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
