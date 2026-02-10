from pathlib import Path
from config import settings
import pandas as pd
from confluent_kafka import Producer
from schema import FeaturesEvent
from datetime import datetime, timezone
import time
from typing import Iterator

class EventGenerator:
    def __init__(self, dataset_path:str) -> None:
        self.producer: Producer = None
        self.dataset_path = Path(dataset_path)
        self.df: pd.DataFrame = None
        self._load_dataset()

    
    def _load_dataset(self):
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found at {self.dataset_path}")
        if self.dataset_path.suffix == ".csv":
            self.df = pd.read_csv(self.dataset_path)
        elif self.dataset_path.suffix == ".json":
            self.df = pd.read_json(self.dataset_path)
        elif self.dataset_path.suffix == ".parquet":
            self.df = pd.read_parquet(self.dataset_path)
        else:
            raise ValueError(f"Unsupported file format: {self.dataset_path.suffix}")
        

    def connect(self) -> None:
        config = {
        "bootstrap.servers": settings.kafka_bootstrap_servers,
        }
        self.producer = Producer(config)
        print(f"Connected to Kafka at {settings.kafka_bootstrap_servers}")


    def get_events(self) -> Iterator [FeaturesEvent]:
        row_index = 0
        total_rows = len(self.df)
        while True:
            row = self.df.iloc[row_index]
            features=row.to_dict()
            features.pop('timestamp', None)
            event = FeaturesEvent(
                timestamp=datetime.now(timezone.utc),
                features=features
            )
            yield event
            row_index = (row_index + 1) % total_rows

    def produce_event(self,event: FeaturesEvent) -> None:
        if not self.producer:
            raise RuntimeError("Producer not connected. Call connect() first.")
        try :
            message = event.model_dump_json().encode("utf-8")
            self.producer.produce(
                topic=settings.kafka_features_topic,
                value=message,
            )
            self.producer.flush() #force sending the message immediately
            print(f"✓ Sent event at {event.timestamp} | Features: {len(event.features)}")
        
        
        except Exception as e:
            print(f"Error producing event: {e}")
    


    def close(self) -> None:
        if self.producer:
            self.producer.flush()  
            print("Kafka producer closed")



    def run(self) -> None:
        print(f"Starting event generator(interval: {settings.generation_interval}s)")
        print(f"Publishing to topic: {settings.kafka_features_topic}")
        try:
            for event in self.get_events():
                self.produce_event(event)
                time.sleep(settings.generation_interval)
        except KeyboardInterrupt:
            print("Event generator stopped by user.")
        finally:
            self.close()

if __name__ == "__main__":
    dataset_path = settings.dataset_path if hasattr(settings, 'dataset_path') else "data/transactions.csv"
        
    generator = EventGenerator(dataset_path)  # 1. Load dataset
    generator.connect()                       # 2. Connect to Kafka
    generator.run()                           # 3. Start sending events
