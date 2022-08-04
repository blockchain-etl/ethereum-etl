import os

POSTGRES_DB_NAME = os.getenv('POSTGRES_SECRET', 'prod/hypernativedb')
OFFSETS_BUCKET = os.getenv('OFFSETS_BUCKET', 'hypernative-offsets')
ETHEREUM_NODE_OFFSETS_PREFIX = os.getenv('ETHEREUM_NODE_OFFSETS_PREFIX', 'ethereum_node_offsets')
NODE_PROVIDER = os.getenv("PROVIDER", "http://44.207.25.161:8584")
