#!/usr/bin/env bash

input_dir=.

usage() { echo "Usage: $0 -s <start_block> -e <end_block> -b <batch_size> [-i <input_dir>]" 1>&2; exit 1; }

while getopts ":s:e:" opt; do
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
            input_dir=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

if [ -z "${start_block}" ] || [ -z "${end_block}" ] || [ -z "${batch_size}" ]; then
    usage
fi

for (( batch_start_block=$start_block; (batch_start_block + batch_size - 1) <= $end_block; batch_start_block+=$batch_size )); do
    batch_end_block=$((batch_start_block + batch_size - 1))
    batch_end_block=$((batch_end_block > end_block ? end_block : batch_end_block))

    padded_batch_start_block=`printf "%08d" ${batch_start_block}`
    padded_batch_end_block=`printf "%08d" ${batch_end_block}`
    file_name_suffix=${padded_batch_start_block}_${padded_batch_end_block}
    # Hive style partitioning
    full_output_dir=${input_dir}/start_block=${padded_batch_start_block}/end_block=${padded_batch_end_block}

    mkdir -p ${full_output_dir};

    old_blocks_file=${input_dir}/blocks_${file_name_suffix}.csv
    new_blocks_file=${full_output_dir}/blocks_${file_name_suffix}.csv
    mv ${old_blocks_file} ${new_blocks_file}

    old_transactions_file=${input_dir}/transactions_${file_name_suffix}.csv
    new_transactions_file=${full_output_dir}/transactions_${file_name_suffix}.csv
    mv ${old_transactions_file} ${new_transactions_file}

    old_erc20_transfers_file=${input_dir}/erc20_transfers_${file_name_suffix}.csv
    new_erc20_transfers_file=${full_output_dir}/erc20_transfers_${file_name_suffix}.csv
    mv ${old_erc20_transfers_file} ${new_erc20_transfers_file}
done
