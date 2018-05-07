#!/usr/bin/env bash

ipc_path=~/Library/Ethereum/geth.ipc
ipc_batch_size=100
export_erc20_batch_size=10000
output_dir=.

current_time() { echo `date '+%Y-%m-%d %H:%M:%S'`; }

log() { echo "$(current_time) ${1}"; }

usage() { echo "Usage: $0 -s <start_block> -e <end_block> -b <batch_size> -i <ipc_path> [-o <output_dir>]" 1>&2; exit 1; }

while getopts ":s:e:b:i:o:" opt; do
    case "${opt}" in
        s)
            start_block=${OPTARG}
            ;;
        e)
            end_block=${OPTARG}
            ;;
        b)
            batch_size=${OPTARG}
            ;;
        i)
            ipc_path=${OPTARG}
            ;;
        o)
            output_dir=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

if [ -z "${start_block}" ] || [ -z "${end_block}" ] || [ -z "${batch_size}" ] || [ -z "${ipc_path}" ]; then
    usage
fi

mkdir -p ${output_dir};

for (( batch_start_block=$start_block; (batch_start_block + batch_size - 1) <= $end_block; batch_start_block+=$batch_size )); do
    start_time=$(date +%s)
    batch_end_block=$((batch_start_block + batch_size - 1))
    batch_end_block=$((batch_end_block > end_block ? end_block : batch_end_block))

    padded_batch_start_block=`printf "%08d" ${batch_start_block}`
    padded_batch_end_block=`printf "%08d" ${batch_end_block}`
    block_range=${padded_batch_start_block}-${padded_batch_end_block}
    file_name_suffix=${padded_batch_start_block}_${padded_batch_end_block}

    blocks_rpc_output_file=${output_dir}/blocks_rpc_output_${file_name_suffix}.json
    log "Exporting blocks ${block_range} to ${blocks_rpc_output_file}"
    python gen_blocks_rpc.py --start-block=${batch_start_block} --end-block=${batch_end_block} | \
    python exchange_with_ipc.py --ipc-path=${ipc_path} --batch-size=${ipc_batch_size} > ${blocks_rpc_output_file}

    blocks_file=${output_dir}/blocks_${file_name_suffix}.csv
    log "Extracting blocks ${block_range} to ${blocks_file}"
    python extract_blocks.py < ${blocks_rpc_output_file} > ${blocks_file}

    transactions_file=${output_dir}/transactions_${file_name_suffix}.csv
    log "Extracting transactions for blocks ${block_range} to ${transactions_file}"
    python extract_transactions.py < ${blocks_rpc_output_file} > ${transactions_file}

    erc20_transfers_file=${output_dir}/erc20_transfers_${file_name_suffix}.csv
    log "Exporting ERC20 transfers for blocks ${block_range} to ${erc20_transfers_file}"
    python export_erc20_transfers.py --start-block=${batch_start_block} --end-block=${batch_end_block} --ipc-path=${ipc_path} --batch-size=${export_erc20_batch_size} > ${erc20_transfers_file}

    end_time=$(date +%s)
    time_diff=$((end_time-start_time))

    log "Exporting blocks ${block_range} took ${time_diff} seconds"
done
