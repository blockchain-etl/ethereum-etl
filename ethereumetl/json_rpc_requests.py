def generate_get_block_by_number_json_rpc(start_block, end_block, include_transactions):
    for idx, block_number in enumerate(range(start_block, end_block + 1)):
        yield generate_json_rpc(
            method='eth_getBlockByNumber',
            params=[hex(block_number), include_transactions],
            request_id=idx
        )


def generate_get_receipt_json_rpc(tx_hashes):
    for idx, tx_hash in enumerate(tx_hashes):
        yield generate_json_rpc(
            method='eth_getTransactionReceipt',
            params=[tx_hash],
            request_id=idx
        )


def generate_get_code_json_rpc(contract_addresses, block='latest'):
    for idx, contract_address in enumerate(contract_addresses):
        yield generate_json_rpc(
            method='eth_getCode',
            params=[contract_address, hex(block) if isinstance(block, int) else block],
            request_id=idx
        )


def generate_json_rpc(method, params, request_id=1):
    return {
        'jsonrpc': '2.0',
        'method': method,
        'params': params,
        'id': request_id,
    }
