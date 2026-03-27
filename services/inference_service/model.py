from __future__ import annotations

import json
from typing import Dict

import joblib
import numpy as np

from config import settings
from schema import PredictionEvent


class IsolationForestModel:
    """
    Loads a trained Isolation Forest model and runs inference.
    """

    def __init__(self) -> None:
        self.model = joblib.load(settings.model_path)

        with open(settings.metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        self.model_name = metadata["model_name"]
        self.model_version = metadata["model_version"]
        self.threshold = metadata.get("threshold", 0.5)
        self.feature_order = metadata["feature_order"]

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