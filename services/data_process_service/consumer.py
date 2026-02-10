from confluent_kafka import Consumer

def create_consumer(bootstrap: str) -> Consumer:
    conf = {
        "bootstrap.servers": bootstrap,
        "group.id": "data-tracking",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
    }
    return Consumer(conf)