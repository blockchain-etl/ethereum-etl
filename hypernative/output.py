from hypernative.aws_secret_provider import AWSSecretProvider
from hypernative.consts import POSTGRES_DB_NAME


def generate_postgres_output():
    secret_provider = AWSSecretProvider()
    cfg = secret_provider.get_secret(POSTGRES_DB_NAME)
    return f"postgresql+pg8000://{cfg['username']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['dbname']}"
