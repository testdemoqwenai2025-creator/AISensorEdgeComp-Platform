"""
AISensorEdgeComp ingest service.

Subscribes to MQTT topics, normalizes to canonical schema, publishes to Kafka.
Exposes /health and /metrics endpoints.

Entry point: python -m services.ingest.main
"""
import asyncio
import logging
import signal
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from prometheus_client import Counter, Histogram, make_asgi_app

from .config import settings
from .mqtt_subscriber import MQTTSubscriber
from .kafka_producer import KafkaProducer
from .canonical import normalize_raw_reading

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
)
log = structlog.get_logger()

# Prometheus metrics
MESSAGES_RECEIVED = Counter("ingest_messages_received_total", "MQTT messages received", ["topic"])
MESSAGES_NORMALIZED = Counter("ingest_messages_normalized_total", "Messages normalized to canonical schema")
MESSAGES_PUBLISHED = Counter("ingest_messages_published_total", "Messages published to Kafka", ["topic"])
MESSAGES_FAILED = Counter("ingest_messages_failed_total", "Failed messages", ["reason"])
NORMALIZE_LATENCY = Histogram("ingest_normalize_latency_seconds", "Time to normalize a message")
KAFKA_PUBLISH_LATENCY = Histogram("ingest_kafka_publish_latency_seconds", "Time to publish to Kafka")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown lifecycle."""
    log.info("ingest.starting", broker=settings.MQTT_BROKER_HOST, kafka=settings.KAFKA_BOOTSTRAP_SERVERS)

    # Start Kafka producer
    producer = KafkaProducer(settings)
    await producer.start()
    app.state.producer = producer

    # Start MQTT subscriber (runs in background)
    subscriber = MQTTSubscriber(settings, on_message=lambda topic, payload: asyncio.create_task(
        handle_message(topic, payload, producer)
    ))
    await subscriber.start()
    app.state.subscriber = subscriber

    log.info("ingest.ready")
    yield

    log.info("ingest.stopping")
    await subscriber.stop()
    await producer.stop()
    log.info("ingest.stopped")

app = FastAPI(
    title="AISensorEdgeComp Ingest",
    version="0.1.0",
    lifespan=lifespan,
)

# Mount Prometheus metrics
app.mount("/metrics", make_asgi_app())

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "ingest",
        "mqtt_connected": app.state.subscriber.is_connected() if hasattr(app.state, "subscriber") else False,
        "kafka_connected": app.state.producer.is_connected() if hasattr(app.state, "producer") else False,
    }

async def handle_message(topic: str, payload: bytes, producer: KafkaProducer):
    """Handle an MQTT message: normalize, publish to Kafka."""
    MESSAGES_RECEIVED.labels(topic=topic).inc()
    try:
        with NORMALIZE_LATENCY.time():
            canonical = await normalize_raw_reading(topic, payload)
        MESSAGES_NORMALIZED.inc()

        with KAFKA_PUBLISH_LATENCY.time():
            await producer.publish(canonical)
        MESSAGES_PUBLISHED.labels(topic=canonical["sensor_id"]).inc()

    except Exception as e:
        MESSAGES_FAILED.labels(reason=type(e).__name__).inc()
        log.error("ingest.message_failed", topic=topic, error=str(e))


def main():
    """Run as a script."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_config=None)


if __name__ == "__main__":
    main()
