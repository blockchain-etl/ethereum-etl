#!/usr/bin/bash

rm last_synced_block_hot.txt

python ethereumetl.py stream --provider-uri http://eth-fast.palantree.com:8545/ -w 15 -B 20 -b 5 --period-seconds 2 -l last_synced_block_hot.txt -s $1 -e transaction,token_transfer -o kafka