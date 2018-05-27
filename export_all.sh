#!/usr/bin/env bash

export_blocks_batch_size=100
export_erc20_batch_size=100
output_dir=.

current_time() { echo `date '+%Y-%m-%d %H:%M:%S'`; }

log() { echo "$(current_time) ${1}"; }

quit_if_returned_error() {
    ret_val=$?
    if [ ${ret_val} -ne 0 ]; then
        log "An error occurred. Quitting."
        exit ${ret_val}
    fi
}

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

for (( batch_start_block=$start_block; batch_start_block <= $end_block; batch_start_block+=$batch_size )); do
    start_time=$(date +%s)
    batch_end_block=$((batch_start_block + batch_size - 1))
    batch_end_block=$((batch_end_block > end_block ? end_block : batch_end_block))

    padded_batch_start_block=`printf "%08d" ${batch_start_block}`
    padded_batch_end_block=`printf "%08d" ${batch_end_block}`
    block_range=${padded_batch_start_block}-${padded_batch_end_block}
    file_name_suffix=${padded_batch_start_block}_${padded_batch_end_block}
    # Hive style partitioning
    full_output_dir=${output_dir}/start_block=${padded_batch_start_block}/end_block=${padded_batch_end_block}

    mkdir -p ${full_output_dir};

    blocks_file=${full_output_dir}/blocks_${file_name_suffix}.csv
    transactions_file=${full_output_dir}/transactions_${file_name_suffix}.csv
    log "Exporting blocks ${block_range} to ${blocks_file}"
    log "Exporting transactions from blocks ${block_range} to ${transactions_file}"
    python3 export_blocks_and_transactions.py --start-block=${batch_start_block} --end-block=${batch_end_block} --ipc-path="${ipc_path}" --batch-size=${export_blocks_batch_size} --blocks-output=${blocks_file} --transactions-output=${transactions_file}
    quit_if_returned_error

    erc20_transfers_file=${full_output_dir}/erc20_transfers_${file_name_suffix}.csv
    log "Exporting ERC20 transfers from blocks ${block_range} to ${erc20_transfers_file}"
    python3 export_erc20_transfers.py --start-block=${batch_start_block} --end-block=${batch_end_block} --ipc-path="${ipc_path}" --batch-size=${export_erc20_batch_size} --output=${erc20_transfers_file}
    quit_if_returned_error

    end_time=$(date +%s)
    time_diff=$((end_time-start_time))

    log "Exporting blocks ${block_range} took ${time_diff} seconds"
done
