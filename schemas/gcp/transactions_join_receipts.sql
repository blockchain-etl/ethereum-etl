SELECT
  blocks.block_timestamp,
  TIMESTAMP_SECONDS(blocks.block_timestamp) as block_timestamp_partition,
  transactions.tx_block_hash,
  transactions.tx_block_number,
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
FROM `ethereumetl.ethereum.blocks` AS blocks
  JOIN `ethereumetl.ethereum.transactions` AS transactions ON blocks.block_number = transactions.tx_block_number
  JOIN `ethereumetl.ethereum.receipts` AS receipts ON transactions.tx_hash = receipts.receipt_transaction_hash