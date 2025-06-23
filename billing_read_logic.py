
def get_billing_record(record_id, partition_key, cosmos_container, blob_container):
    try:
        return cosmos_container.read_item(item=record_id, partition_key=partition_key)
    except:
        blob_name = f"{record_id}.json"
        blob_client = blob_container.get_blob_client(blob_name)
        if blob_client.exists():
            return json.loads(blob_client.download_blob().readall())
        else:
            return None
