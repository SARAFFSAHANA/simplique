
import datetime
import azure.functions as func
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient

def main(mytimer: func.TimerRequest) -> None:
    COSMOS_ENDPOINT = "https://<account>.documents.azure.com"
    COSMOS_KEY = "<key>"
    DATABASE_NAME = "BillingDB"
    CONTAINER_NAME = "Records"

    BLOB_CONNECTION_STRING = "<blob-conn-string>"
    BLOB_CONTAINER_NAME = "archived-billing-records"

    cosmos_client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
    blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
    blob_container = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)

    container = cosmos_client.get_database_client(DATABASE_NAME).get_container_client(CONTAINER_NAME)

    archive_date = (datetime.datetime.utcnow() - datetime.timedelta(days=90)).isoformat()

    query = f"SELECT * FROM c WHERE c.date < '{archive_date}'"
    for record in container.query_items(query, enable_cross_partition_query=True):
        record_id = record['id']
        partition_key = record['partitionKey']
        blob_name = f"{record_id}.json"
        blob_container.upload_blob(name=blob_name, data=str(record), overwrite=True)
        container.delete_item(item=record_id, partition_key=partition_key)
