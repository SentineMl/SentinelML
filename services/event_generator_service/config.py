from pydantic_settings import BaseSettings
from pathlib import Path 

class Settings(BaseSettings):
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_features_topic: str = "raw_events"
    generation_interval: float = 1.0
    dataset_path: str =  str(Path(__file__).parent / "data" / "transactions.csv")
    offset_file: str = str(Path(__file__).parent / "offset.txt")  # File to persist current offset
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "sentinel"
    db_user: str = "sentinel_user"
    db_password: str = "sentinel_pass"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


    class Config:
        env_file = ".env"

settings = Settings()