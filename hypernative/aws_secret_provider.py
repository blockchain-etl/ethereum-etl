import json

import boto3


SERVICE_NAME = "secretsmanager"
SECRET_MANAGER_URL = "https://secretsmanager.us-east-1.amazonaws.com"
SECRET_STRING = "SecretString"
SECRET_LIST = "SecretList"


class AWSSecretProvider:
    def __init__(self, *_, **kwargs):
        super().__init__(**kwargs)
        self.region = kwargs.get("region", "us-east-1")
        self._init_client(kwargs.get("session"))

    def _init_client(self, session):
        if session is None:
            session = boto3.session.Session()
        self._client = session.client(
            service_name=SERVICE_NAME, region_name=self.region, endpoint_url=SECRET_MANAGER_URL
        )

    def get_secret(self, secret_name: str, *_, **kwargs):
        try:
            return json.loads(self._client.get_secret_value(SecretId=secret_name).get(SECRET_STRING, "{}"))
        except self._client.exceptions.ResourceNotFoundException:
            return None

    def put_secret(self, secret_name: str, secret_value: dict, *_, **kwargs):
        string_value = json.dumps(secret_value)
        try:
            self._client.create_secret(
                Name=secret_name, SecretString=string_value, Description=kwargs.get("description", "")
            )
        except self._client.exceptions.ResourceExistsException:
            return False
        return True

    def update_secret(self, secret_name: str, secret_value: dict, *_, **kwargs):
        string_value = json.dumps(secret_value)
        try:
            self._client.put_secret_value(SecretId=secret_name, SecretString=string_value)
        except self._client.exceptions.ResourceNotFoundException:
            return False
        return True

    def get_all_secrets_names(self, *_, **kwargs):
        return self._client.list_secrets().get(SECRET_LIST, [])

    # Didn't implement delete_secret in order to prevent deletions by mistake, better using AWS api for deleting
