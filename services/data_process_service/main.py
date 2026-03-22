# services/process-data/main.py
import json
import os
from datetime import datetime, timezone



from consumer import create_consumer
from producer import create_producer, send_json
from data_processing import process_event

#juste default values
BOOTSTRAP = os.getenv("BOOTSTRAP_SERVERS", "kafka1:9092")
IN_TOPIC = os.getenv("IN_TOPIC", "raw_events")
OUT_TOPIC = os.getenv("OUT_TOPIC", "features")

def main():
    consumer = create_consumer(BOOTSTRAP)
    producer = create_producer(BOOTSTRAP)

    consumer.subscribe([IN_TOPIC])
    print(f"✅ processing {IN_TOPIC} -> {OUT_TOPIC}")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            # 1) decode raw event
            try:
                raw_event = json.loads(msg.value().decode("utf-8"))
            except Exception as e:
                print(f"Bad JSON, skipping. err={e}")
                # commit to avoid being stuck on bad message forever
                consumer.commit(message=msg, asynchronous=False)
                continue

            # 2) process -> features
            try:
                features = process_event(raw_event)
            except Exception as e:
                print(f"Processing failed, skipping. err={e}")
                consumer.commit(message=msg, asynchronous=False)
                continue

            key = features.get("customer_id") or features.get("transaction_id")

            event = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "features": features
            }

            print("SENDING TO FEATURES TOPIC:", event)
            send_json(producer, OUT_TOPIC, event, key=key)

        

            consumer.commit(message=msg, asynchronous=False)

    except KeyboardInterrupt:
        print("Stopping...")

    finally:
        producer.flush(10)
        consumer.close()

if __name__ == "__main__":
    main()