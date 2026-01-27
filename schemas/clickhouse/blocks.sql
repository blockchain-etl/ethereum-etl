CREATE TABLE IF NOT EXISTS blocks
(
    `number`            Int64,
    `hash`              String,
    `parent_hash`       String,
    `nonce`             String,
    `sha3_uncles`       String,
    `logs_bloom`        String,
    `transactions_root` String,
    `state_root`        String,
    `receipts_root`     String,
    `miner`             String,
    `difficulty`        Decimal(38, 0),
    `total_difficulty`  Decimal(38, 0),
    `size`              Int64,
    `extra_data`        String,
    `gas_limit`         Int64,
    `gas_used`          Int64,
    `timestamp`         Int64,
    `transaction_count` Int64,
    `base_fee_per_gas`  Int64
)
    ENGINE = MergeTree() ORDER BY (timestamp)
