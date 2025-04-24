from datetime import timedelta

from feast import Entity, FeatureView, Field
from feast.infra.offline_stores.contrib.clickhouse_offline_store.clickhouse_source import (
    ClickhouseSource,
)
from feast.types import Float64, Int64

nodes_source = ClickhouseSource(
    name="nodes", table="feature_data.nodes_agg", timestamp_field="event_timestamp"
)

node = Entity(name="node", join_keys=["entity_id"])

nodes_fv = FeatureView(
    name="nodes_agg",
    entities=[node],
    ttl=timedelta(days=1),
    schema=[
        Field(name="spot_node_count", dtype=Int64),
        Field(name="avg_spot_node_age", dtype=Float64),
    ],
    source=nodes_source,
    online=True,
)
