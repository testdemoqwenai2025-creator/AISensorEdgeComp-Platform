"""Real-time TS-FM inference server. Loads ONNX model, runs anomaly detection."""
import asyncio
import logging
from pathlib import Path

import onnxruntime as ort
from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, make_asgi_app
import numpy as np

log = logging.getLogger(__name__)
app = FastAPI(title="TS-FM Inference")
app.mount("/metrics", make_asgi_app())

PREDICTIONS_TOTAL = Counter("ml_predictions_total", "Inferences run", ["sensor_kind"])
PREDICTIONS_FAILED = Counter("ml_predictions_failed_total", "Failed inferences", ["reason"])
INFERENCE_LATENCY = Histogram("ml_inference_latency_seconds", "Time per inference")

class Session:
    def __init__(self):
        self.env = ort.get_environment()
        # In production: load from ML_MODEL_PATH env var
        self.session = ort.InferenceSession(str(Path("ml/models/ts-fm-v1.onnx")))

session: Session | None = None

@app.on_event("startup")
async def startup():
    global session
    log.info("inference.starting")
    session = Session()
    log.info("inference.ready")

class AnomalyRequest(BaseModel):
    sensor_id: str
    sensor_kind: str
    window: list[float]  # quantile-tokenized window

class AnomalyResponse(BaseModel):
    sensor_id: str
    anomaly_score: float
    confidence: float
    model_version: str

@app.post("/api/v1/infer/anomaly", response_model=AnomalyResponse)
async def infer_anomaly(req: AnomalyRequest):
    PREDICTIONS_TOTAL.labels(sensor_kind=req.sensor_kind).inc()
    with INFERENCE_LATENCY.time():
        try:
            input_ids = np.array([req.window], dtype=np.int64)
            logits = session.session.run(None, {"input_ids": input_ids})[0]
            # Simplified: anomaly score = max logit / sum
            probs = np.exp(logits[0]) / np.exp(logits[0]).sum(axis=-1, keepdims=True)
            anomaly_score = float(probs.max())
            confidence = 0.85 + 0.1 * float(probs.std())
            return AnomalyResponse(
                sensor_id=req.sensor_id,
                anomaly_score=anomaly_score,
                confidence=confidence,
                model_version="ts-fm-v1",
            )
        except Exception as e:
            PREDICTIONS_FAILED.labels(reason=type(e).__name__).inc()
            raise
