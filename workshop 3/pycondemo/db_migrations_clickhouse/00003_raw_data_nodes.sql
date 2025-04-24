-- +goose NO TRANSACTION
-- +goose Up
-- +goose StatementBegin
CREATE TABLE raw_data.`nodes`
(
    `id` String,
    `name` String,
    `created_at` DateTime64(6),
    `interrupted_at` Nullable(DateTime64(6)),
    `deleted_at` Nullable(DateTime64(6)),
    `cloud` Nullable(String),
    `instance_type` Nullable(String),
    `is_spot` Nullable(Bool),
    `region` LowCardinality(String),
    `cpu_count` Int32,
    `memory_gb` Int32,
    `event_timestamp` DateTime64(6)
)
ENGINE = MergeTree()
ORDER BY (id)
;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE raw_data.`clusters.nodes`
;
-- +goose StatementEnd
