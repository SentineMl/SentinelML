from __future__ import annotations

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		case_sensitive=False,
		extra="ignore",
	)

	# Kafka
	kafka_bootstrap_servers: str = Field(
		default="localhost:9092",
		description="Kafka bootstrap servers (comma-separated).",
	)
	kafka_group_id: str = Field(
		default="inference-service",
		description="Consumer group id.",
	)
	kafka_features_topic: str = Field(
		default="features",
		description="Input topic for feature events.",
	)
	kafka_predictions_topic: str = Field(
		default="predictions",
		description="Output topic for predictions.",
	)
	kafka_auto_offset_reset: str = Field(
		default="latest",
		description="Kafka consumer offset reset policy.",
	)

	model_path: str = str(BASE_DIR / "artifacts" / "model.joblib")
	metadata_path: str = str(BASE_DIR / "artifacts" / "metadata.json")
	mlflow_tracking_uri: str = Field(
		default="http://mlflow-server:5000",
		description="MLflow tracking URI used to access the model registry.",
	)
	mlflow_registry_model_name: str = Field(
		default="fraud-isolation-forest",
		description="Registered MLflow model name.",
	)
	mlflow_registry_model_version: str = Field(
		default="1",
		description="MLflow model version (used when alias is not provided).",
	)
	mlflow_registry_model_alias: str | None = Field(
		default=None,
		description="Optional MLflow model alias (for example: 'champion').",
	)
	default_threshold: float = Field(
		default=0.5,
		description="Fallback anomaly threshold when not provided by registry tags.",
	)
	# Database
	db_host: str = Field(default="localhost", description="PostgreSQL host.")
	db_port: int = Field(default=5432, description="PostgreSQL port.")
	db_name: str = Field(default="sentinel", description="PostgreSQL database name.")
	db_user: str = Field(default="sentinel_user", description="PostgreSQL user.")
	db_password: str = Field(default="sentinel_pass", description="PostgreSQL password.")

	@property
	def database_url(self) -> str:
		return (
			f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
			f"@{self.db_host}:{self.db_port}/{self.db_name}"
		)


settings = Settings()
