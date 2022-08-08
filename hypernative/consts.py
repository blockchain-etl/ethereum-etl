import os

POSTGRES_DB_NAME = os.getenv('POSTGRES_SECRET', 'prod/hypernativedb')
ETHEREUM_ETL_BUCKET = os.getenv('ETHEREUM_ETL_BUCKET', 'hypernative-ethereumetl')
OFFSETS_BUCKET = os.getenv('OFFSETS_BUCKET', 'hypernative-offsets')
ETHEREUM_NODE_OFFSETS_PREFIX = os.getenv('ETHEREUM_NODE_OFFSETS_PREFIX', 'ethereum_node_offsets')
NODE_PROVIDER = os.getenv("PROVIDER", "http://44.207.25.161:8584")
ETHEREUM_ETL_ATHENA_DB_NAME = os.getenv('ETHEREUM_ETL_ATHENA_DB_MAME', "ethereum_etl")
