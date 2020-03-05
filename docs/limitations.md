# Limitation

- In case the contract is a proxy, which forwards all calls to a delegate, interface detection doesn’t work,
which means `is_erc20` and `is_erc721` will always be false for proxy contracts and they will be missing in the `tokens`
table.
- The metadata methods (`symbol`, `name`, `decimals`, `total_supply`) for ERC20 are optional, so around 10% of the
contracts are missing this data. Also some contracts (EOS) implement these methods but with wrong return type,
so the metadata columns are missing in this case as well.
- `token_transfers.value`, `tokens.decimals` and `tokens.total_supply` have type `STRING` in BigQuery tables,
because numeric types there can't handle 32-byte integers. You should use
`cast(value as FLOAT64)` (possible loss of precision) or
`safe_cast(value as NUMERIC)` (possible overflow) to convert to numbers.
- The contracts that don't implement `decimals()` function but have the
[fallback function](https://solidity.readthedocs.io/en/v0.4.21/contracts.html#fallback-function) that returns a `boolean`
will have `0` or `1` in the `decimals` column in the CSVs.