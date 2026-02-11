from __future__ import annotations

import json
from typing import Optional

from confluent_kafka import Producer

from config import settings
from schema import PredictionEvent


class PredictionProducer:
    """
    Produces prediction events to Kafka topic.
    """

    def __init__(self) -> None:
        self.producer: Optional[Producer] = None

    def connect(self) -> None:
        """Initialize Kafka producer connection."""
        config = {
            "bootstrap.servers": settings.kafka_bootstrap_servers,
        }
        self.producer = Producer(config)

    def produce(self, prediction: PredictionEvent) -> None:
        """
        Send a prediction event to Kafka.
        
        Args:
            prediction: PredictionEvent to publish.
        """
        if not self.producer:
            raise RuntimeError("Producer not connected. Call connect() first.")

        try:
            message = prediction.model_dump_json().encode("utf-8")
            self.producer.produce(
                topic=settings.kafka_predictions_topic,
                value=message,
            )
            self.producer.flush()
        except Exception as e:
            print(f"Error producing message: {e}")

    def close(self) -> None:
        """Close the Kafka producer connection."""
        if self.producer:
            self.producer.flush()
            self.producer.close()
