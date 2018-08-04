SELECT
  blocks.timestamp,
  TIMESTAMP_SECONDS(blocks.timestamp) as timestamp_partition,
  blocks.hash,
  blocks.number,
  transactions.hash,
  transactions.nonce,
  transactions.index,
  transactions.from_address,
  transactions.to_address,
  transactions.value,
  transactions.gas,
  transactions.gas_price,
  transactions.input,
  receipts.receipt_cumulative_gas_used,
  receipts.receipt_gas_used,
  receipts.receipt_contract_address,
  receipts.receipt_root,
  receipts.receipt_status
FROM `ethereum.blocks` AS blocks
  JOIN `ethereum.transactions` AS transactions ON blocks.number = transactions.block_number
  JOIN `ethereum.receipts` AS receipts ON transactions.hash = receipts.receipt_transaction_hash