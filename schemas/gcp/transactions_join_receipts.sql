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
  receipts.cumulative_gas_used,
  receipts.gas_used,
  receipts.contract_address,
  receipts.root,
  receipts.status
FROM `ethereum.blocks` AS blocks
  JOIN `ethereum.transactions` AS transactions ON blocks.number = transactions.block_number
  JOIN `ethereum.receipts` AS receipts ON transactions.hash = receipts.transaction_hash