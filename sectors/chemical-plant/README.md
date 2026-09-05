# AISensorEdgeComp — Chemical Plant Sector Configuration

Reactor + distillation + storage tank monitoring

## Buyer
Plant managers, process safety engineers

## Sensor modalities used
- vibration
- temperature
- pressure
- gas
- flow
- vision

## Compliance
OSHA PSM (29 CFR 1910.119), EPA RMP, IEC 61511 (SIS)

## ROI benchmarks
−60% unplanned reactor trips, −25% energy waste

## Reference architecture
Edge clusters per process unit + centralized cloud control; safety-critical inferences always run on-device (TS-FM at edge); SIL-2 certified gateway options

## Files in this directory
- `config.yaml` — sector-specific config overrides
- `docker-compose.yml` — sector-specific docker compose (uses base + overrides)
- `k8s/` — sector-specific k8s manifests
- `dashboards/` — Grafana dashboards pre-built for this sector

## Try it
```bash
# Deploy this sector config
make deploy-sector SECTOR=chemical-plant NAMESPACE=production
```

See the [main platform README](../../README.md) for general info.
