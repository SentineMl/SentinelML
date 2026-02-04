from __future__ import annotations

import json
from typing import Optional

from confluent_kafka import Consumer

from inference_service.config import settings
from inference_service.schema import featuresEvent


class FeatureConsumer:
    """
    Consumes feature events from Kafka topic.
    """

    def __init__(self) -> None:
        self.consumer: Optional[Consumer] = None

    def connect(self) -> None:
        """Initialize Kafka consumer connection."""
        config = {
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "group.id": settings.kafka_group_id,
            "auto.offset.reset": settings.kafka_auto_offset_reset,
            "enable.auto.commit": True,
        }
        self.consumer = Consumer(config)
        self.consumer.subscribe([settings.kafka_features_topic])

    def consume(self):
        """
        Consume messages from Kafka and yield validated FeatureEvent objects.
        """
        if not self.consumer:
            raise RuntimeError("Consumer not connected. Call connect() first.")

        while True:
            msg = self.consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                continue

            try:
                value = json.loads(msg.value().decode("utf-8"))
                event = featuresEvent(**value)
                yield event
            except Exception as e:
                print(f"Error processing message: {e}")
                continue

    def close(self) -> None:
        """Close the Kafka consumer connection."""
        if self.consumer:
            self.consumer.close()
