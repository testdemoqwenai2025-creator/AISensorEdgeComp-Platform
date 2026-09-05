# AISensorEdgeComp — Water Treatment Sector Configuration

Intake + treatment + distribution sensor intelligence

## Buyer
Municipal water utilities, industrial water users, water-tech companies

## Sensor modalities used
- pressure
- flow
- temperature
- vision
- chemical

## Compliance
Safe Drinking Water Act, EPA Lead and Copper Rule, ISO 24528

## ROI benchmarks
−25% non-revenue water, +40% water quality compliance

## Reference architecture
Per-treatment-plant edge cluster; distribution mesh with LoRaWAN; cloud tenant per utility; self-calibration mesh for low-maintenance sensor networks

## Files in this directory
- `config.yaml` — sector-specific config overrides
- `docker-compose.yml` — sector-specific docker compose (uses base + overrides)
- `k8s/` — sector-specific k8s manifests
- `dashboards/` — Grafana dashboards pre-built for this sector

## Try it
```bash
# Deploy this sector config
make deploy-sector SECTOR=water-treatment NAMESPACE=production
```

See the [main platform README](../../README.md) for general info.
