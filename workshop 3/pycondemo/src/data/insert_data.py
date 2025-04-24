from random import randint

import pandas as pd

from db_utils.clickhouse import get_clickhouse_client
from data.generate_data import generate_node_metadata


def insert_sample_data():
    ch_client = get_clickhouse_client()

    spot_nodes = [generate_node_metadata(i) for i in range(randint(500, 2000))]
    df = pd.DataFrame(spot_nodes)
    ch_client.insert_df(table="nodes", database="raw_data", df=df)


if __name__ == "__main__":
    insert_sample_data()
