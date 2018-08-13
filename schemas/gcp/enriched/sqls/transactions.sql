SELECT
    transactions.hash,
    transactions.nonce,
    transactions.transaction_index,
    transactions.from_address,
    transactions.to_address,
    transactions.value,
    transactions.gas,
    transactions.gas_price,
    transactions.input,
    receipts.cumulative_gas_used AS receipt_cumulative_gas_used,
    receipts.gas_used AS receipt_gas_used,
    receipts.contract_address AS receipt_contract_address,
    receipts.root AS receipt_root,
    receipts.status AS receipt_status,
    TIMESTAMP_SECONDS(blocks.timestamp) AS block_timestamp,
    blocks.number AS block_number,
    blocks.hash AS block_hash
FROM ethereum_blockchain_raw.blocks AS blocks
    JOIN ethereum_blockchain_raw.transactions AS transactions ON blocks.number = transactions.block_number
    JOIN ethereum_blockchain_raw.receipts AS receipts ON transactions.hash = receipts.transaction_hash