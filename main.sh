#!/bin/bash

NAME="${HN_JOB_NAME:=default}"
JOB_NUM_JOBS="${HN_BATCH_JOB_ARRAY_SIZE:=0}"
NODE_INDEX="${AWS_BATCH_JOB_ARRAY_INDEX:=0}"
START_BLOCK_INDEX="${HN_START_BLOCK_INDEX:=-1}"
END_BLOCK_INDEX="${HN_END_BLOCK_INDEX:=-1}"
BATCH_SIZE="${HN_BATCH_SIZE:=100}"
BLOCK_BATCH_SIZE="${HN_BLOCK_BATCH_SIZE:=1}"
OUTPUT="${HN_OUTPUT:=postgres}"

PROVIDER_ARR=("http://44.207.25.161:8584" "http://44.209.138.14:8584" "http://44.208.109.105:8584")
PROVIDER_INDEX=$(( NODE_INDEX % 3 ))
PROVIDER="${PROVIDER_ARR[$PROVIDER_INDEX]}"

echo "Arg configuration: --job-name ${NAME} \
                         --start-block-index ${START_BLOCK_INDEX} \
                         --end-block-index ${END_BLOCK_INDEX} \
                         --nodes ${JOB_NUM_JOBS} \
                         --node-index ${NODE_INDEX} \
                         --provider-uri ${PROVIDER} \
                         --batch-size $BATCH_SIZE \
                         --block-batch-size $BLOCK_BATCH_SIZE \
                         --output $OUTPUT"

python /ethereum-etl/main.py --job-name ${NAME} \
                             --start-block-index ${START_BLOCK_INDEX} \
                             --end-block-index ${END_BLOCK_INDEX} \
                             --nodes ${JOB_NUM_JOBS} \
                             --node-index ${NODE_INDEX} \
                             --provider-uri "${PROVIDER}" \
                             --batch-size $BATCH_SIZE \
                             --block-batch-size $BLOCK_BATCH_SIZE \
                             --output $OUTPUT
