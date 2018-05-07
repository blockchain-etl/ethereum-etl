#!/usr/bin/env bash

start_block=0
end_block=1000000
batch_size=100000
geth_ipc_path=~/Library/Ethereum/geth.ipc
ipc_batch_size=100

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

    padded_batch_start_block=`printf "%08d" ${batch_start_block}`
    padded_batch_end_block=`printf "%08d" ${batch_end_block}`
    file_name_suffix=${padded_batch_start_block}_${padded_batch_end_block}

    blocks_rpc_output_file=blocks_rpc_output_${file_name_suffix}.json
    echo "Exporting blocks ${padded_batch_start_block}-${padded_batch_end_block} to ${blocks_rpc_output_file}"
    python gen_blocks_rpc.py --start-block=${batch_start_block} --end-block=${batch_end_block} | \
    python exchange_with_ipc.py --ipc-path=${geth_ipc_path} --batch-size=${ipc_batch_size} > ${blocks_rpc_output_file}

    blocks_file=blocks_${file_name_suffix}.csv
    echo "Extracting blocks ${padded_batch_start_block}-${padded_batch_end_block} to ${blocks_file}"
    python extract_blocks.py < ${blocks_rpc_output_file} > ${blocks_file}

    transactions_file=transactions_${file_name_suffix}.csv
    echo "Extracting transactions for blocks ${padded_batch_start_block}-${padded_batch_end_block} to ${transactions_file}"
    python extract_transactions.py < ${blocks_rpc_output_file} > ${transactions_file}

    transaction_receipts_rpc_output_file=transaction_receipts_rpc_output_${file_name_suffix}.json
    echo "Exporting transaction receipts for blocks ${padded_batch_start_block}-${padded_batch_end_block} to ${transaction_receipts_rpc_output_file}"
    python extract_csv_column.py --input=${transactions_file} --column=tx_hash | \
    python gen_transaction_receipts_rpc.py | \
    python exchange_with_ipc.py --ipc-path=${geth_ipc_path} --batch-size=${ipc_batch_size} > ${transaction_receipts_rpc_output_file}

    erc20_transfers_file=erc20_transfers_${file_name_suffix}.csv
    echo "Extracting ERC20 transfers for blocks ${padded_batch_start_block}-${padded_batch_end_block} to ${erc20_transfers_file}"
    python extract_erc2_transfers.py < ${transaction_receipts_rpc_output_file} > ${erc20_transfers_file}
done