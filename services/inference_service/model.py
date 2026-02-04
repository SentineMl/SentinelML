from __future__ import annotations

import random
from typing import Dict

from inference_service.schema import PredictionEvent


class DummyModel:
    """
    A dummy ML model for testing inference.
    """

    def __init__(self, model_name: str = "dummy-model", model_version: str = "v1") -> None:
        self.model_name = model_name
        self.model_version = model_version
        self.anomaly_threshold = 0.7

    def predict(self, features: Dict[str, float]) -> PredictionEvent:
        """
        Generate a dummy prediction based on input features.
        
        Args:
            features: Dictionary of feature values.
            
        Returns:
            A PredictionEvent with random anomaly score.
        """
        anomaly_score = random.random()
        is_anomaly = anomaly_score >= self.anomaly_threshold
        
        return PredictionEvent(
            anomaly_score=anomaly_score,
            is_anomaly=is_anomaly,
            model_name=self.model_name,
            model_version=self.model_version,
        )
