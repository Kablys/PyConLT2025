-- +goose NO TRANSACTION
-- +goose Up
-- +goose StatementBegin
CREATE DATABASE raw_data
;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP DATABASE raw_data
;
-- +goose StatementEnd
