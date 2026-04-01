from __future__ import annotations

import json
from typing import Dict

import mlflow
import numpy as np

from config import settings
from schema import PredictionEvent


class IsolationForestModel:
    """
    Loads a trained Isolation Forest model and runs inference.
    """

    def __init__(self) -> None:
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        model_uri = (
            f"models:/{settings.mlflow_registry_model_name}"
            f"/{settings.mlflow_registry_model_version}"
        )

        # Pull and deserialize the model from MLflow Registry (simplest path).
        self.model = mlflow.sklearn.load_model(model_uri)
        metadata = self._load_fallback_metadata()

        self.model_name = settings.mlflow_registry_model_name
        self.model_version = f"v{settings.mlflow_registry_model_version}"
        self.threshold = float(metadata.get("threshold", settings.default_threshold))
        self.feature_order = metadata["feature_order"]

    def _load_fallback_metadata(self) -> Dict:
        with open(settings.metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _prepare_features(self, features: Dict[str, float]) -> np.ndarray:
        row = [features.get(feature_name, 0.0) for feature_name in self.feature_order]
        return np.array([row], dtype=float)

    def predict(self, features: Dict[str, float]) -> PredictionEvent:
        x = self._prepare_features(features)

        raw_score = self.model.decision_function(x)[0]
        anomaly_score = float(-raw_score)

        is_anomaly = anomaly_score >= self.threshold

        return PredictionEvent(
            anomaly_score=anomaly_score,
            is_anomaly=is_anomaly,
            model_name=self.model_name,
            model_version=self.model_version,
        )