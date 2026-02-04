from __future__ import annotations

from inference_service.consumer import FeatureConsumer
from inference_service.producer import PredictionProducer
from inference_service.model import DummyModel


def main() -> None:
    """
    Main inference loop: consume feature events, run model, produce predictions.
    """
    consumer = FeatureConsumer()
    producer = PredictionProducer()
    model = DummyModel()

    try:
        consumer.connect()
        producer.connect()

        print("Starting inference service...")
        for feature_event in consumer.consume():
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
