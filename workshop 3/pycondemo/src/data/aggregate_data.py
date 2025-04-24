from db_utils.clickhouse import get_clickhouse_client


def aggregate_data():
    ch_client = get_clickhouse_client()

    nodes_aggregation_df = ch_client.query_df("""
        SELECT
            now() AS event_timestamp,
            cloud || '_' || region || '_' || instance_type AS entity_id,
            count(*) AS spot_node_count,
            avg(dateDiff('minute', created_at, now())) AS avg_spot_node_age
        FROM raw_data.nodes
        WHERE is_spot 
            AND event_timestamp > now() - interval 5 minute
        GROUP BY cloud, instance_type, region
    """)

    ch_client.insert_df(
        table="nodes_agg", database="feature_data", df=nodes_aggregation_df
    )


if __name__ == "__main__":
    aggregate_data()
