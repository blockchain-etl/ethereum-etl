SELECT
  blocks.block_timestamp,
  TIMESTAMP_SECONDS(blocks.block_timestamp) as block_timestamp_partition,
  blocks.block_hash,
  blocks.block_number,
  transactions.tx_hash,
  transactions.tx_nonce,
  transactions.tx_index,
  transactions.tx_from,
  transactions.tx_to,
  transactions.tx_value,
  transactions.tx_gas,
  transactions.tx_gas_price,
  transactions.tx_input,
  receipts.receipt_cumulative_gas_used,
  receipts.receipt_gas_used,
  receipts.receipt_contract_address,
  receipts.receipt_root,
  receipts.receipt_status
FROM `ethereum.blocks` AS blocks
  JOIN `ethereum.transactions` AS transactions ON blocks.block_number = transactions.tx_block_number
  JOIN `ethereum.receipts` AS receipts ON transactions.tx_hash = receipts.receipt_transaction_hash