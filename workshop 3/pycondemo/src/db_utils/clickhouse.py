import os

from clickhouse_connect import create_client


def get_clickhouse_client():
    return create_client(
        host=os.environ.get("CLICKHOUSE_HOST", "localhost"),
        username=os.environ.get("CLICKHOUSE_USER", ""),
        password=os.environ.get("CLICKHOUSE_PASSWORD", "password"),
        database=os.environ.get("CLICKHOUSE_DATABASE", "raw_data"),
        port=int(os.environ.get("CLICKHOUSE_PORT", "8123")),
    )
