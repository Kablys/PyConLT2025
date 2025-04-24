import os

import mlflow
import pandas as pd
import requests
from fastapi import FastAPI, HTTPException
from feast import FeatureStore
from loguru import logger
from pydantic import BaseModel

app = FastAPI(title="Spot Interruption Prediction API")
store = FeatureStore(repo_path=os.getenv("FEAST_REPO_PATH", "."))

mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000"))
model = mlflow.sklearn.load_model("models:/spot_interruption_model@champion")
required_features = [feature for feature in model.feature_names_in_]
feast_features = [feature.replace("__", ":") for feature in required_features]


class PredictionRequest(BaseModel):
    entity_id: str


class PredictionResponse(BaseModel):
    entity_id: str
    prediction: float


class HTTPFeaturesRequest(BaseModel):
    entity_id: str


class HTTPFeaturesResponse(BaseModel):
    entity_id: str
    features: dict


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/predict/python-sdk", response_model=PredictionResponse)
async def predict_python_sdk(request: PredictionRequest):
    try:
        features = store.get_online_features(
            features=feast_features,
            entity_rows=[{"entity_id": request.entity_id}],
            full_feature_names=True,
        ).to_df()

        X = features[required_features]
        prediction = model.predict_proba(X)[0][1]

        return PredictionResponse(
            entity_id=request.entity_id,
            prediction=float(prediction),
        )
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/http", response_model=PredictionResponse)
async def predict_http(request: PredictionRequest):
    try:
        feast_server_url = os.environ.get("FEAST_SERVER_URL", "http://localhost:6566")
        response = requests.post(
            f"{feast_server_url}/get-online-features",
            json={
                "features": feast_features,
                "entities": {"entity_id": [request.entity_id]},
                "full_feature_names": True,
            },
        )
        if response.status_code != 200:
            logger.error(f"Failed to fetch features from Feast server: {response.text}")
            raise HTTPException(
                status_code=500, detail="Failed to fetch features from Feast server"
            )

        features_data = response.json()
        feature_indices = {
            feature: features_data["metadata"]["feature_names"].index(feature)
            for feature in required_features
        }
        features = pd.DataFrame(
            {
                feature: [features_data["results"][idx]["values"][0]]
                for feature, idx in feature_indices.items()
            }
        )
        prediction = model.predict_proba(features)[0][1]

        return PredictionResponse(
            entity_id=request.entity_id,
            prediction=float(prediction),
        )
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
