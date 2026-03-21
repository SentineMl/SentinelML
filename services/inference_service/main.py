from __future__ import annotations

from consumer import FeatureConsumer
from producer import PredictionProducer
from model import DummyModel
from config import settings

from orm import create_session_factory, init_schema, save_prediction


def main() -> None:
    """
    Main inference loop: consume feature events, run model, produce predictions.
    """
    consumer = FeatureConsumer()
    producer = PredictionProducer()
    model = DummyModel()
    init_schema(settings.database_url)
    session_factory = create_session_factory(settings.database_url)
    db_session = session_factory()

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

            transaction_id = None
            if feature_event.features:
                transaction_id = feature_event.features.get("transaction_id")
            if transaction_id:
                save_prediction(
                    db_session,
                    transaction_id=str(transaction_id),
                    score=float(prediction.anomaly_score),
                    prediction_timestamp=prediction.timestamp,
                )
            else:
                print("Skipping prediction persistence: transaction_id missing in event payload")

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        db_session.close()
        consumer.close()
        producer.close()


if __name__ == "__main__":
    main()
