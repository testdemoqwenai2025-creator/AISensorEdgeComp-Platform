"""AISensorEdgeComp ML inference service.

Consumes telemetry from Kafka, runs TS-FM anomaly detection, emits anomaly tokens.
Also serves RUL predictions on request.
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any
import structlog

log = structlog.get_logger()

app = FastAPI(title="AISensorEdgeComp ML", version="0.1.0")

@app.on_event("startup")
async def startup():
    log.info("ml.starting")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ml"}

class InferenceRequest(BaseModel):
    sensor_id: str
    window: list[float]  # last N samples
    sensor_kind: str

@app.post("/api/v1/infer/anomaly")
async def infer_anomaly(req: InferenceRequest) -> dict[str, Any]:
    """Run TS-FM anomaly detection on a window of samples."""
    # In production: load ONNX model, run inference
    return {
        "sensor_id": req.sensor_id,
        "anomaly_score": 0.0,
        "confidence": 0.0,
        "model_version": "ts-fm-v1",
    }

@app.post("/api/v1/infer/rul")
async def infer_rul(req: InferenceRequest) -> dict[str, Any]:
    """Predict remaining useful life for an asset."""
    return {
        "sensor_id": req.sensor_id,
        "rul_hours": None,
        "confidence": 0.0,
        "model_version": "rul-v1",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
