import datetime
from typing import Dict
from pydantic import BaseModel, Field

class FeaturesEvent(BaseModel):
    timestamp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        description="Event timestamp (UTC)."
    )
    features: Dict[str, float] = Field(
        ...,
        min_length=1,
        description="Flat numeric feature vector used by the model."
    )


class PredictionEvent(BaseModel):
    """
    Message produced by inference-service to Kafka topic: `predictions`.
    """

    timestamp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        description="Prediction timestamp (UTC)."
    )
    anomaly_score: float = Field(
        ...,
        ge=0.0,
        description="Anomaly score (higher = more anomalous)."
    )
    is_anomaly: bool = Field(
        ...,
        description="True if anomaly_score crosses the configured threshold."
    )
    model_name: str = Field(
        ...,
        min_length=1,
        description="Registered model name (e.g., 'anomaly-detector')."
    )
    model_version: str = Field(
        ...,
        min_length=1,
        description="Model version identifier (e.g., 'v3' or MLflow version)."
    )