#!/usr/bin/bash

rm last_synced_block_warm.txt

python ethereumetl.py stream --provider-uri http://eth-fast.palantree.com:8545/ -w 35 -b 10 -B 10 --period-seconds 5  -l last_synced_block_warm.txt -s $1 --lag 18 -e transaction,token_transfer -o kafka  -t eth.hot