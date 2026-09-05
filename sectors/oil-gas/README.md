# AISensorEdgeComp — Oil & Gas Sector Configuration

Upstream + midstream + downstream sensor intelligence

## Buyer
Operators, pipeline companies, refineries

## Sensor modalities used
- vibration
- pressure
- temperature
- gas
- flow

## Compliance
API 1160, PHMSA, OSHA 1910

## ROI benchmarks
−42% unplanned downtime, −18% HSE incidents

## Reference architecture
Edge clusters at each wellpad + pipeline compressor station; cloud control plane for cross-asset reasoning; air-gapped option for offshore rigs

## Files in this directory
- `config.yaml` — sector-specific config overrides
- `docker-compose.yml` — sector-specific docker compose (uses base + overrides)
- `k8s/` — sector-specific k8s manifests
- `dashboards/` — Grafana dashboards pre-built for this sector

## Try it
```bash
# Deploy this sector config
make deploy-sector SECTOR=oil-gas NAMESPACE=production
```

See the [main platform README](../../README.md) for general info.
