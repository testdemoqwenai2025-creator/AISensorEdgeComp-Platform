"""AISensorEdgeComp API server — REST endpoints for sensors, alerts, RUL."""
import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="AISensorEdgeComp API", version="0.1.0")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "api"}

@app.get("/api/v1/sensors")
async def list_sensors():
    """List all known sensors with current state."""
    # In production: query TimescaleDB
    return {"sensors": [], "count": 0}

@app.get("/api/v1/sensors/{sensor_id}/readings")
async def get_readings(sensor_id: str, since: int = 0, limit: int = 1000):
    """Get raw readings for a sensor since a timestamp."""
    # In production: query TimescaleDB
    return {"sensor_id": sensor_id, "readings": [], "count": 0}

@app.get("/api/v1/alerts")
async def list_alerts(severity: str | None = None, limit: int = 100):
    """List recent alerts, optionally filtered by severity."""
    return {"alerts": [], "count": 0}

@app.get("/api/v1/assets/{asset_id}/rul")
async def get_rul(asset_id: str):
    """Get remaining-useful-life prediction for an asset."""
    return {"asset_id": asset_id, "rul_hours": None, "confidence": None}

@app.get("/api/v1/search")
async def search(q: str):
    """LLM-native natural language search (delegates to ml service)."""
    return {"query": q, "answer": "TODO: delegate to ml service", "citations": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
