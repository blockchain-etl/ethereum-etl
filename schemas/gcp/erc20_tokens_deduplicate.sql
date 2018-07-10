WITH erc20_tokens_grouped AS (
  SELECT
    erc20_token_address,
    erc20_token_symbol,
    erc20_token_name,
    erc20_token_decimals,
    erc20_token_total_supply,
    ROW_NUMBER() OVER (PARTITION BY erc20_token_address) AS rank
  FROM
    `ethereum.erc20_tokens_duplicates`)
SELECT
  erc20_token_address,
  erc20_token_symbol,
  erc20_token_name,
  erc20_token_decimals,
  erc20_token_total_supply
FROM erc20_tokens_grouped
WHERE erc20_tokens_grouped.rank = 1
