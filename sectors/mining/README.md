# AISensorEdgeComp — Mining Sector Configuration

Surface + underground + processing plant operations

## Buyer
Mining operators, equipment OEMs, processing plants

## Sensor modalities used
- vibration
- gas
- temperature
- pressure
- vision

## Compliance
MSHA 30 CFR, ISO 19434 (mine hazard classification)

## ROI benchmarks
−45% unplanned truck downtime, −60% methane evacuation response time

## Reference architecture
Per-site edge cluster with mesh networking for underground; satellite backhaul for remote sites; air quality mesh with self-calibration; per-shift asset tracking

## Files in this directory
- `config.yaml` — sector-specific config overrides
- `docker-compose.yml` — sector-specific docker compose (uses base + overrides)
- `k8s/` — sector-specific k8s manifests
- `dashboards/` — Grafana dashboards pre-built for this sector

## Try it
```bash
# Deploy this sector config
make deploy-sector SECTOR=mining NAMESPACE=production
```

See the [main platform README](../../README.md) for general info.
