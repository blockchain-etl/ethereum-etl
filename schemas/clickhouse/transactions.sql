CREATE TABLE IF NOT EXISTS transactions (
    `hash` String,
    `nonce` Int64,
    `block_hash` String,
    `block_number` Int64,
    `transaction_index` Int64,
    `from_address` String,
    `to_address` Nullable(String),
    `value` Decimal(38, 0),
    `gas` Int64,
    `gas_price` Int64,
    `input` String,
    `block_timestamp` Int64,
    `max_fee_per_gas` Nullable(Int64),
    `max_priority_fee_per_gas` Nullable(Int64),
    `transaction_type` Int64
) ENGINE = MergeTree() ORDER BY (block_timestamp)
