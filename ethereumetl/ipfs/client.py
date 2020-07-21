import logging
import requests

logger = logging.getLogger('ipfs')

IPFS_TIMEOUT = 5  # Timeout in second
IPFS_NUM_ATTEMPTS = 3

# A simple client to fetch content from IPFS gateways.
class IpfsClient:
    def __init__(self, gatewayUrls):
        self._gatewayUrls = gatewayUrls

    def _get(self, path, json):
        for i in range(IPFS_NUM_ATTEMPTS):
            # Round-robin thru the gateways.
            gatewayUrl = self._gatewayUrls[i % len(self._gatewayUrls)]
            try:
                url = "{}/{}".format(gatewayUrl, path)
                r = requests.get(url, timeout=IPFS_TIMEOUT)
                r.raise_for_status()
                return r.json() if json else r.text
            except Exception as e:
                logger.error("Attempt #{} - Failed downloading {}: {}".format(i + 1, path, e))
        raise Exception("IPFS download failure for hash {}".format(path))

    def get(self, path):
        return self._get(path, False)

    def get_json(self, path):
        return self._get(path, True)
