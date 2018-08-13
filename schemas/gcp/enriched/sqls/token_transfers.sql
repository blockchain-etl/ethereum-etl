SELECT
    token_transfers.token_address,
    token_transfers.from_address,
    token_transfers.to_address,
    token_transfers.value,
    token_transfers.transaction_hash,
    token_transfers.log_index,
    TIMESTAMP_SECONDS(blocks.timestamp) AS block_timestamp,
    blocks.number AS block_number,
    blocks.hash AS block_hash
FROM ethereum_blockchain_raw.blocks AS blocks
    JOIN ethereum_blockchain_raw.token_transfers AS token_transfers ON blocks.number = token_transfers.block_number