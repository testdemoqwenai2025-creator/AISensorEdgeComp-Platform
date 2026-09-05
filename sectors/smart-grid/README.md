# AISensorEdgeComp — Smart Grid Sector Configuration

Generation + transmission + distribution sensor intelligence

## Buyer
Utilities, ISO/RTOs, distributed energy operators

## Sensor modalities used
- vibration
- temperature
- current
- voltage
- phasor

## Compliance
NERC CIP, IEC 61850, IEEE 1547 (distributed gen)

## ROI benchmarks
−30% SAIDI/SAIFI, +18% renewable curtailment reduction

## Reference architecture
Substation edge clusters (TSN-enabled); control center cloud tenant; protective relay integration via IEC 61850; sub-100ms inference for protective actions

## Files in this directory
- `config.yaml` — sector-specific config overrides
- `docker-compose.yml` — sector-specific docker compose (uses base + overrides)
- `k8s/` — sector-specific k8s manifests
- `dashboards/` — Grafana dashboards pre-built for this sector

## Try it
```bash
# Deploy this sector config
make deploy-sector SECTOR=smart-grid NAMESPACE=production
```

See the [main platform README](../../README.md) for general info.
