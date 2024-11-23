import os
from azure.cosmos import CosmosClient, exceptions
from dotenv import load_dotenv
import uuid
import random

# Load environment variables
load_dotenv()

# Primary DB Configuration
PRIMARY_DB_ENDPOINT = os.getenv("COSMOSDB_PRIMARY_ENDPOINT")
PRIMARY_DB_KEY = os.getenv("COSMOSDB_PRIMARY_KEY")
PRIMARY_DB_NAME = os.getenv("COSMOSDB_DATABASE")
PRIMARY_CONTAINER_NAME = os.getenv("COSMOSDB_PRIMARY_CONTAINER")

# Secondary DB Configuration
SECONDARY_DB_ENDPOINT = os.getenv("COSMOSDB_SECONDARY_ENDPOINT")
SECONDARY_DB_KEY = os.getenv("COSMOSDB_SECONDARY_KEY")
SECONDARY_DB_NAME = os.getenv("COSMOSDB_DATABASE")
SECONDARY_CONTAINER_NAME = os.getenv("COSMOSDB_SECONDARY_CONTAINER")

# Initialize CosmosDB Clients
primary_client = CosmosClient(PRIMARY_DB_ENDPOINT, credential=PRIMARY_DB_KEY)
secondary_client = CosmosClient(SECONDARY_DB_ENDPOINT, credential=SECONDARY_DB_KEY)

# Get Containers
primary_container = primary_client.get_database_client(PRIMARY_DB_NAME).get_container_client(PRIMARY_CONTAINER_NAME)
secondary_container = secondary_client.get_database_client(SECONDARY_DB_NAME).get_container_client(SECONDARY_CONTAINER_NAME)

def save_to_primary(data):
    """
    Save a new session to the primary database.
    """
    try:
        primary_container.create_item(body=data)
        print(f"Saved to primary DB: {data['id']}")
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error saving to primary DB: {e}")
        raise

def update_secondary(data):
    """
    Update or insert a summary in the secondary database.
    If user_id and file_name match, update the document; otherwise, create a new one.
    """
    try:
        query = f"SELECT * FROM c WHERE c.user_id = {data['user_id']} AND c.file_name = '{data['file_name']}'"
        items = list(secondary_container.query_items(query=query, enable_cross_partition_query=True))

        if items:
            # Update existing document
            existing_item = items[0]
            existing_item["tasks_summary"].append({
                "task": data["task"],
                "extracted_data": data["extracted_data"],
                "timestamp": data["upload_timestamp"],
                "Pages selected": data["Pages selected"]
            })
            secondary_container.replace_item(item=existing_item, body=existing_item)
            print(f"Updated secondary DB for user_id: {data['user_id']}, file_name: {data['file_name']}")
        else:
            # Insert new document
            new_item = {
                "user_id": data["user_id"],
                "id": f"summary-{data['id']}",
                "file_name": data["file_name"],
                "tasks_summary": [
                    {
                        "task": data["task"],
                        "extracted_data": data["extracted_data"],
                        "timestamp": data["upload_timestamp"],
                        "Pages selected": data["Pages selected"]
                    }
                ]
            }
            secondary_container.create_item(body=new_item)
            print(f"Created new document in secondary DB for user_id: {data['user_id']}, file_name: {data['file_name']}")
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error updating secondary DB: {e}")
        raise
