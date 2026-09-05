"""Normalize raw MQTT payloads to the canonical measurement schema.

See: schemas/avro/telemetry.avsc and schemas/proto/telemetry.proto for the contract.
"""
import json
import time
import uuid
from typing import Any

from structlog import get_logger

log = get_logger()


async def normalize_raw_reading(topic: str, payload: bytes) -> dict[str, Any]:
    """Convert an MQTT message into a canonical measurement record.

    Args:
        topic: MQTT topic, e.g. "aisensor/telemetry/plant_a/line3/compressor_a/vibration"
        payload: MQTT payload (JSON bytes)
    Returns:
        Canonical measurement record (see schemas/avro/telemetry.avsc).
    """
    # Parse topic to extract sensor metadata
    parts = topic.split("/")
    if len(parts) < 4:
        raise ValueError(f"Invalid topic structure: {topic}")
    sensor_id = "/".join(parts[2:-1])  # e.g. plant_a/line3/compressor_a/vibration

    # Parse payload
    try:
        raw = json.loads(payload)
    except json.JSONDecodeError:
        raise ValueError(f"Payload is not valid JSON: {payload[:64]}")

    # Required fields
    if "value" not in raw or "unit" not in raw:
        raise ValueError(f"Payload missing required fields (value, unit): {raw}")

    # Compose canonical record
    canonical = {
        "measurement_id": f"meas_{uuid.uuid4().hex[:24]}",
        "sensor_id": sensor_id.replace("/", "_"),
        "sensor_kind": raw.get("sensor_kind", _infer_kind(topic)),
        "physical_quantity": raw.get("physical_quantity", parts[-1]),
        "unit": raw["unit"],
        "value": float(raw["value"]),
        "uncertainty": float(raw.get("uncertainty", 0.0)),
        "timestamp_ns": int(raw.get("timestamp_ns", time.time_ns())),
        "sample_rate_hz": float(raw.get("sample_rate_hz", 1.0)),
        "location": raw.get("location", {}),
        "lineage": {
            "ingest_protocol": "mqtt",
            "source_node_id": topic,
            "ingest_ts": time.time_ns(),
            "calibration_age_days": int(raw.get("calibration_age_days", 0)),
        },
        "calibration_confidence": float(raw.get("calibration_confidence", 1.0)),
    }
    return canonical


def _infer_kind(topic: str) -> str:
    """Heuristic: infer sensor_kind from topic suffix."""
    last = topic.split("/")[-1].lower()
    kind_map = {
        "vibration": "vibration",
        "temperature": "temperature",
        "temp": "temperature",
        "pressure": "pressure",
        "flow": "flow",
        "gas": "gas",
        "humidity": "humidity",
        "ph": "ph",
        "ec": "ec",
    }
    return kind_map.get(last, "unknown")
