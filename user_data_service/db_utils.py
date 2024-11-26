import os
from azure.cosmos import CosmosClient, exceptions
from dotenv import load_dotenv

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

