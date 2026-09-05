# AISensorEdgeComp — Autonomous Vehicles Sector Configuration

Fleet health monitoring, perception sensor analytics, safety event recording

## Buyer
Fleet operators, AV software companies, Tier-1 suppliers

## Sensor modalities used
- vision
- mmwave
- vibration
- temperature
- pressure

## Compliance
ISO 26262 (ASIL-D), SAE J3016, UN-R155 cybersecurity

## ROI benchmarks
−55% fleet downtime, −30% collision-related maintenance cost

## Reference architecture
Per-vehicle edge (Jetson Orin NX + Hailo-8); fleet-level cloud with strong isolation; OTA model updates via signed bundles; 100ms inference SLA for safety-critical

## Files in this directory
- `config.yaml` — sector-specific config overrides
- `docker-compose.yml` — sector-specific docker compose (uses base + overrides)
- `k8s/` — sector-specific k8s manifests
- `dashboards/` — Grafana dashboards pre-built for this sector

## Try it
```bash
# Deploy this sector config
make deploy-sector SECTOR=autonomous-vehicles NAMESPACE=production
```

See the [main platform README](../../README.md) for general info.
