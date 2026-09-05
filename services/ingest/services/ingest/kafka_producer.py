"""Async Kafka producer using aiokafka, with Avro serialization."""
import json
import logging
from typing import Any

from aiokafka import AIOKafkaProducer
from structlog import get_logger

from .config import settings

log = get_logger()


class KafkaProducer:
    """Async Kafka producer. Serializes canonical measurements as JSON
    (in production: Avro via Schema Registry — see schemas/avro/telemetry.avsc)."""

    def __init__(self, settings):
        self.settings = settings
        self.producer: AIOKafkaProducer | None = None

    async def start(self):
        log.info("kafka.connecting", brokers=self.settings.KAFKA_BOOTSTRAP_SERVERS)
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.settings.KAFKA_BOOTSTRAP_SERVERS,
            client_id=self.settings.KAFKA_CLIENT_ID,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            acks="all",
            enable_idempotence=True,
            compression_type="zstd",
        )
        await self.producer.start()
        log.info("kafka.ready")

    async def stop(self):
        if self.producer:
            await self.producer.stop()
            log.info("kafka.stopped")

    def is_connected(self) -> bool:
        return self.producer is not None

    async def publish(self, canonical: dict[str, Any]):
        """Publish a canonical measurement to Kafka."""
        topic = self.settings.KAFKA_TOPIC_TELEMETRY
        key = canonical["sensor_id"]
        await self.producer.send_and_wait(topic, canonical, key=key)
        log.debug("kafka.published", topic=topic, key=key)
