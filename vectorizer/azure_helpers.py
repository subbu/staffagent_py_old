import os
import uuid
from decouple import config
from azure.storage.blob import BlobServiceClient


def upload_to_blob_storage():
    try:
        connection_string = str(config('AZURE_ACCOUNT_URI'))
        container_name = str(config('CONTAINER_NAME'))
        # print(connection_string, container_name)

        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string)
        container_client = blob_service_client.get_container_client(
            container_name)

        blob_name = str(uuid.uuid4())
        blob_client = container_client.get_blob_client(blob_name)
        file_path = "resume.pdf"
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data)
        blob_uri = blob_client.url
        return blob_uri
    except Exception as e:
        print(f"Error uploading to Azure Blob Storage: {e}")
        return None


def download_from_blob_storage(blob_uri):
    try:
        CURRENT_WORKING_DIR = os.getcwd()
        TARGET_DIR = os.path.join(CURRENT_WORKING_DIR, "uploads")
        if not os.path.exists(TARGET_DIR):
            os.makedirs(TARGET_DIR)

        parts = blob_uri.split('/')
        container_name = parts[-2]
        blob_name = parts[-1]

        blob_service_client = BlobServiceClient.from_connection_string(
            config('AZURE_ACCOUNT_URI'))
        container_client = blob_service_client.get_container_client(
            container_name)

        blob_client = container_client.get_blob_client(blob_name)

        target_path = os.path.join(TARGET_DIR, str(blob_name)+'.pdf')
        with open(target_path, "wb") as data:
            data.write(blob_client.download_blob().readall())
        return True

    except Exception as e:
        print(f"Error downloading from Azure Blob Storage: {e}")
        return False
