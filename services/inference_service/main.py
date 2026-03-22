from __future__ import annotations

from consumer import FeatureConsumer
from producer import PredictionProducer
from model import IsolationForestModel


def main() -> None:
    """
    Main inference loop: consume feature events, run model, produce predictions.
    """
    consumer = FeatureConsumer()
    producer = PredictionProducer()
    model = IsolationForestModel()

    try:
        consumer.connect()
        producer.connect()

        print("Starting inference service...")
        for feature_event in consumer.consume():
            print(f"Received feature event: {feature_event}")
            # Run inference
            prediction = model.predict(
                features=feature_event.features,
            )

            # Produce prediction
            producer.produce(prediction)
            print(f"Produced prediction: {prediction.anomaly_score:.2f}")

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        consumer.close()
        producer.close()


if __name__ == "__main__":
    main()
