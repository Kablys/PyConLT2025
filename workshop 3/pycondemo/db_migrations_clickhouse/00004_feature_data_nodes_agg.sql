-- +goose NO TRANSACTION
-- +goose Up
-- +goose StatementBegin
CREATE TABLE feature_data.`nodes_agg`
(
    `event_timestamp` DateTime64(6),
    `entity_id` String,
    `spot_node_count` Int32,
    `avg_spot_node_age` Float64,
)
ENGINE = MergeTree()
ORDER BY (entity_id, event_timestamp)
;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE feature_data.`nodes_agg`
;
-- +goose StatementEnd
