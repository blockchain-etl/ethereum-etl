import json

from ethereumetl.utils import hex_to_dec


class MockIPCWrapper(object):
    def __init__(self, read_resource):
        self.read_resource = read_resource

    def make_request(self, text):
        batch = json.loads(text)
        ipc_response = []
        for req in batch:
            if req['method'] == 'eth_getBlockByNumber':
                block_number = hex_to_dec(req['params'][0])
                file_name = 'ipc_response.block.' + str(block_number) + '.json'
            else:
                tx_hash = req['params'][0]
                file_name = 'ipc_response.receipt.' + str(tx_hash) + '.json'
            file_content = self.read_resource(file_name)
            ipc_response.append(json.loads(file_content))
        return ipc_response