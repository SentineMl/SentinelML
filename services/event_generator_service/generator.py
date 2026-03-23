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
        self.offset_file = Path(settings.offset_file)
        self.current_offset = 0
        self._load_dataset()
        self._load_offset()

    
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
    
    def _load_offset(self):
        """Load the last saved offset from file"""
        if self.offset_file.exists():
            try:
                with open(self.offset_file, 'r') as f:
                    self.current_offset = int(f.read().strip())
                print(f"Resuming from saved offset: {self.current_offset}")
            except Exception as e:
                print(f"Could not load offset, starting from 0: {e}")
                self.current_offset = 0
        else:
            print("No saved offset found, starting from 0")
            self.current_offset = 0
    
    def _save_offset(self):
        """Save the current offset to file"""
        try:
            with open(self.offset_file, 'w') as f:
                f.write(str(self.current_offset))
        except Exception as e:
            print(f"Error saving offset: {e}")

    def connect(self) -> None:
        config = {
        "bootstrap.servers": settings.kafka_bootstrap_servers,
        }
        self.producer = Producer(config)
        print(f"Connected to Kafka at {settings.kafka_bootstrap_servers}")


    def get_events(self) -> Iterator [FeaturesEvent]:
        total_rows = len(self.df)
        
        # Validate offset
        if self.current_offset >= total_rows:
            print(f"Warning: Saved offset ({self.current_offset}) exceeds total rows ({total_rows}). Resetting to 0.")
            self.current_offset = 0
        
        while True:
            row = self.df.iloc[self.current_offset]
            features=row.to_dict()
            event = FeaturesEvent(
                features=features
            )
            yield event
            self.current_offset = (self.current_offset + 1) % total_rows
            # Save offset every 10 events to avoid excessive I/O
            if self.current_offset % 10 == 0:
                self._save_offset()

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
            print(f"✓ Sent event | Features: {len(event.features)}")
        
        
        except Exception as e:
            print(f"Error producing event: {e}")
    


    def close(self) -> None:
        if self.producer:
            self.producer.flush()  
            print("Kafka producer closed")
        # Save the final offset before closing
        self._save_offset()
        print(f"Saved offset: {self.current_offset}")



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
