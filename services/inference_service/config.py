from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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


settings = Settings()
