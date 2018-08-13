SELECT
    logs.log_index,
    logs.transaction_hash,
    logs.transaction_index,
    logs.address,
    logs.data,
    logs.topics,
    TIMESTAMP_SECONDS(blocks.timestamp) AS block_timestamp,
    blocks.number AS block_number,
    blocks.hash AS block_hash
FROM ethereum_blockchain_raw.blocks AS blocks
    JOIN ethereum_blockchain_raw.logs AS logs ON blocks.number = logs.block_number