import json as JSON

class MockIpfsClient:
    def __init__(self, read_resource):
        self.read_resource = read_resource

    def _get(self, path, json):
        ipfs_path= "ipfs_" + path.replace('/', '_')
        data = self.read_resource(ipfs_path)
        return JSON.loads(data) if json else data

    def get(self, path):
        return self._get(path, False)

    def get_json(self, path):
        return self._get(path, True)