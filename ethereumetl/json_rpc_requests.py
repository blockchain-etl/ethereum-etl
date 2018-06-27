def generate_get_block_by_number_json_rpc(start_block, end_block, include_transactions):
    for block_number in range(start_block, end_block + 1):
        yield generate_json_rpc('eth_getBlockByNumber', [hex(block_number), include_transactions])


def generate_get_receipt_by_tx_hash_json_rpc(tx_hashes):
    for tx_hash in tx_hashes:
        yield generate_json_rpc('eth_getTransactionReceipt', [tx_hash])


def generate_json_rpc(method, params, id=1):
    return {
        'jsonrpc': '2.0',
        'method': method,
        'params': params,
        'id': id,
    }
