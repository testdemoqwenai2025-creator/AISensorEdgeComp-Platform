# AISensorEdgeComp — Hospital ICU Sector Configuration

Patient monitoring, ventilator analytics, clinical alerting

## Buyer
Hospitals, integrated delivery networks, telemedicine providers

## Sensor modalities used
- vibration
- temperature
- pressure
- gas
- vision

## Compliance
HIPAA, FDA 510(k) for medical device data, IEC 62304

## ROI benchmarks
−38% alarm fatigue, +22% early sepsis detection rate

## Reference architecture
Per-patient edge cluster (Jetson Orin Nano); per-hospital cloud tenant with strict PHI isolation; air-gapped option for inpatient deployments

## Files in this directory
- `config.yaml` — sector-specific config overrides
- `docker-compose.yml` — sector-specific docker compose (uses base + overrides)
- `k8s/` — sector-specific k8s manifests
- `dashboards/` — Grafana dashboards pre-built for this sector

## Try it
```bash
# Deploy this sector config
make deploy-sector SECTOR=hospital-icu NAMESPACE=production
```

See the [main platform README](../../README.md) for general info.
