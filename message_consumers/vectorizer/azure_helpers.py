import os
from decouple import config
from azure.storage.blob import BlobServiceClient


def download_from_blob_storage(blob_uri) -> bool:
    try:
        CURRENT_WORKING_DIR = os.getcwd()
        TARGET_DIR = os.path.join(CURRENT_WORKING_DIR, "uploads")
        if not os.path.exists(TARGET_DIR):
            os.makedirs(TARGET_DIR)

        parts = blob_uri.split('/')
        container_name = parts[-2]
        blob_name = parts[-1]

        AZURE_ACCOUNT_URI = f"DefaultEndpointsProtocol={config('DefaultEndpointsProtocol')};AccountName={config('AccountName')};AccountKey={config('AccountKey')}==;EndpointSuffix={config('EndpointSuffix')}"
        blob_service_client = BlobServiceClient.from_connection_string(
            AZURE_ACCOUNT_URI)
        container_client = blob_service_client.get_container_client(
            container_name)
        blob_client = container_client.get_blob_client(blob_name)
        target_path = os.path.join(TARGET_DIR, str(blob_name))
        with open(target_path, "wb") as data:
            data.write(blob_client.download_blob().readall())
        return True

    except Exception as e:
        print(f"Error downloading from Azure Blob Storage: {e}")
        return False
