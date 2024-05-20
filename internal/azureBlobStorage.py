from azure.storage.blob import BlobServiceClient
from os import getenv

account_name = getenv("STORAGE_ACCOUNT_NAME")
sas_token = getenv("STORAGE_ACCOUNT_SAS_TOKEN")

account_url = f"https://{account_name}.blob.core.windows.net"

blob_service_client = BlobServiceClient(account_url=account_url, credential=sas_token)