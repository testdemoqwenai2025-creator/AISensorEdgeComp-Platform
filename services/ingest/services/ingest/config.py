"""Application configuration, loaded from environment."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", case_sensitive=True)

    # MQTT
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_BROKER_TLS: bool = False
    MQTT_USERNAME: str | None = None
    MQTT_PASSWORD: str | None = None
    MQTT_TOPIC_PREFIX: str = "aisensor/telemetry"
    MQTT_QOS: int = 1
    MQTT_KEEPALIVE: int = 60

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_TELEMETRY: str = "telemetry.raw"
    KAFKA_CLIENT_ID: str = "aisensoredgecomp-ingest"
    KAFKA_SECURITY_PROTOCOL: str = "PLAINTEXT"

    # General
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"


settings = Settings()
