"""Send a test telemetry message via MQTT for local testing."""
import json
import time
import random
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("localhost", 1883, 60)

topic = "aisensor/telemetry/plant_a/line3/compressor_a/vibration"
payload = {
    "value": round(random.uniform(3.5, 5.5), 2),
    "unit": "mm/s_RMS",
    "sample_rate_hz": 10000,
    "uncertainty": 0.05,
    "calibration_age_days": 42,
    "calibration_confidence": 0.97,
}
client.publish(topic, json.dumps(payload), qos=1)
print(f"Published to {topic}: {payload}")
client.disconnect()
