import os

import mlflow
import mlflow.sklearn
import pandas as pd
from feast import FeatureStore
from loguru import logger
from mlflow.models.signature import infer_signature
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

from db_utils.clickhouse import get_clickhouse_client

FEAST_FEATURE_NAMES = ["nodes_agg:spot_node_count", "nodes_agg:avg_spot_node_age"]
FEATURE_COLUMNS = [name.replace(":", "__") for name in FEAST_FEATURE_NAMES]


def get_training_data():
    fs = FeatureStore(repo_path=os.environ.get("FEAST_REPO_PATH", "/home/features"))

    ch_client = get_clickhouse_client()

    logger.info("Fetching raw data from ClickHouse")
    raw_data_df = ch_client.query_df("""
        SELECT
            cloud || '_' || region || '_' || instance_type AS entity_id,
            event_timestamp,
            CASE WHEN interrupted_at IS NOT NULL THEN 1 ELSE 0 END AS label
        FROM raw_data.nodes
        WHERE is_spot
            AND event_timestamp > now() - interval 30 day
        LIMIT 10000
    """)
    logger.info(f"Retrieved {len(raw_data_df)} records from raw data")

    raw_data_df["event_timestamp"] = pd.to_datetime(
        raw_data_df["event_timestamp"]
    ).dt.tz_localize("UTC")

    logger.info("Fetching features from Feast")

    # Point-in-time joins!
    training_df = fs.get_historical_features(
        entity_df=raw_data_df[["entity_id", "event_timestamp"]],
        features=FEAST_FEATURE_NAMES,
        full_feature_names=True,
    ).to_df()
    logger.info(f"Retrieved {len(training_df)} records with features")

    training_df = training_df.merge(
        raw_data_df[["entity_id", "event_timestamp", "label"]],
        on=["entity_id", "event_timestamp"],
    )

    return training_df


def train_model():
    training_df = get_training_data()

    X = training_df[FEATURE_COLUMNS]
    y = training_df["label"]

    logger.info("Splitting data into train and test sets")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    logger.info(f"Training set size: {len(X_train)}, Test set size: {len(X_test)}")

    mlflow.set_tracking_uri(
        os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")
    )
    with mlflow.start_run():
        logger.info("Training RandomForestClassifier")
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        mlflow.log_params({"n_estimators": 100, "random_state": 42, "test_size": 0.2})

        logger.info("Evaluating model")
        y_pred = model.predict(X_test)
        report = classification_report(y_test, y_pred, output_dict=True)
        logger.info("Model Evaluation:\n{}", report)

        mlflow.log_metrics(
            {
                "accuracy": report["accuracy"],
                "precision": report["1"]["precision"],
                "recall": report["1"]["recall"],
                "f1": report["1"]["f1-score"],
            }
        )
        signature = infer_signature(X_train, model.predict(X_train))
        mlflow.sklearn.log_model(
            model,
            "spot_interruption_model",
            signature=signature,
            input_example=X_train.iloc[:5],
        )

        model_details = mlflow.register_model(
            f"runs:/{mlflow.active_run().info.run_id}/spot_interruption_model",
            "spot_interruption_model"
        )
        client = mlflow.tracking.MlflowClient()
        client.set_registered_model_alias(
            "spot_interruption_model",
            "champion",
            model_details.version
        )
        logger.info(f"Registered model version {model_details.version} with champion alias")


if __name__ == "__main__":
    train_model()
