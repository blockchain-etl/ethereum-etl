def generate_get_block_by_number_json_rpc(start_block, end_block, include_transactions):
    for block_number in range(start_block, end_block + 1):
        yield {
            'jsonrpc': '2.0',
            'method': 'eth_getBlockByNumber',
            'params': [hex(block_number), include_transactions],
            'id': 1,
        }