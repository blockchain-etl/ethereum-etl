#!/usr/bin/env bash

start_block=0
end_block=1000000
batch_size=100000
geth_ipc_path=~/Library/Ethereum/geth.ipc

if [ "$1" != "" ]; then
    start_block=$1
fi

if [ "$2" != "" ]; then
    end_block=$2
fi

if [ "$3" != "" ]; then
    batch_size=$3
fi

if [ "$4" != "" ]; then
    geth_ipc_path=$4
fi

for (( batch_start_block=$start_block; (batch_start_block + batch_size - 1) <= $end_block; batch_start_block+=$batch_size )); do
    batch_end_block=$((batch_start_block + batch_size - 1))
    output_file=blocks_rpc_${batch_end_block}_output.json
    echo "Exporting blocks ${batch_start_block}-${batch_end_block} to ${output_file}"
    python gen_blocks_rpc.py --start-block=${batch_start_block} --end-block=${batch_end_block} | nc -U ${geth_ipc_path} > blocks_rpc_${batch_end_block}_output.json
done