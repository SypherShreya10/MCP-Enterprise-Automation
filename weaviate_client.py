from weaviate import connect_to_local

_client = None

def get_client():
    global _client
    if _client is None:
        _client = connect_to_local(skip_init_checks=True)
    return _client

def close_client():
    global _client
    if _client:
        _client.close()
        _client = None
