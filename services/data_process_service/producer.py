import json
import uuid
from confluent_kafka import Producer  

def create_producer(bootstrap: str) -> Producer:
    return Producer({"bootstrap.servers": bootstrap})

def delivery_report(err, msg):
    if err:
        print(f"Delivery failed: {err}")
    else:
        print(f"Delivered to {msg.topic()}[{msg.partition()}]@{msg.offset()}")

def send_json(producer, topic, payload):
    producer.produce(
        topic=topic,
        value=json.dumps(payload).encode(),
        callback=delivery_report
    )
    producer.poll(0)


