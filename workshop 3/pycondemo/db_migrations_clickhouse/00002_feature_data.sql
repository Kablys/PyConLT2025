-- +goose NO TRANSACTION
-- +goose Up
-- +goose StatementBegin
CREATE DATABASE feature_data
;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP DATABASE feature_data
;
-- +goose StatementEnd
