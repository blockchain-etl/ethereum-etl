#!/usr/bin/bash

rm last_synced_block_warm.txt

python ethereumetl.py stream --provider-uri https://patient-quiet-water.quiknode.pro/cbf46386e585531f903652184d07ca49e58cddaa -w 5 -B 20 -b 5 --period-seconds 5 -l last_synced_block_warm.txt -s $1 --lag 18 -e transaction,token_transfer,trace -o kafka -t eth.warm