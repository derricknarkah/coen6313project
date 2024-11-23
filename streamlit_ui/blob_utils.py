from azure.storage.blob import BlobServiceClient
import os

# Initialize Blob Service Client
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

def upload_to_blob(container_name, blob_name, data):
    """
    Uploads data to Azure Blob Storage.
    """
    try:
        # Get the blob client
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        # Upload the file
        blob_client.upload_blob(data, overwrite=True)
        print(f"Uploaded {blob_name} to {container_name}")
    except Exception as e:
        print(f"Error uploading to Blob Storage: {e}")
        raise
