#!/usr/bin/bash

rm last_synced_block.txt

python ethereumetl.py stream --provider-uri http://eth-fast.palantree.com:8545/ -s $1 -e transaction,token_transfer -o kafka