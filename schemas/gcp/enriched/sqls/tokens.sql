WITH tokens_grouped AS (
    SELECT
        address,
        symbol,
        name,
        decimals,
        total_supply,
        ROW_NUMBER() OVER (PARTITION BY address) AS rank
    FROM
        ethereum_blockchain_raw.tokens)
SELECT
    address,
    symbol,
    name,
    decimals,
    total_supply
FROM tokens_grouped
WHERE tokens_grouped.rank = 1
