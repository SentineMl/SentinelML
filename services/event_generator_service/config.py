from pydantic_settings import BaseSettings
from pathlib import Path 

class Settings(BaseSettings):
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_features_topic: str = "features"
    generation_interval: float = 1.0
    dataset_path: str =  str(Path(__file__).parent / "data" / "transactions.csv")


    class Config:
        env_file = ".env"

settings = Settings()