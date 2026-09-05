# AISensorEdgeComp — Sector Configurations

The platform is sector-agnostic, but each vertical has its own deployment
profile. This directory contains the per-sector configurations.

| Sector | Config dir | Compliance |
|--------|-------------|------------|
| Oil & Gas | `oil-gas/` | API 1160, PHMSA, OSHA 1910 |
| Chemical Plant | `chemical-plant/` | OSHA PSM, EPA RMP, IEC 61511 |
| Hospital ICU | `hospital-icu/` | HIPAA, FDA 510(k), IEC 62304 |
| Autonomous Vehicles | `autonomous-vehicles/` | ISO 26262, SAE J3016, UN-R155 |
| Smart Grid | `smart-grid/` | NERC CIP, IEC 61850, IEEE 1547 |
| Mining | `mining/` | MSHA 30 CFR, ISO 19434 |
| Water Treatment | `water-treatment/` | SDWA, EPA LCR, ISO 24528 |

## Using a sector config

```bash
# Deploy for a specific sector
make deploy-sector SECTOR=oil-gas NAMESPACE=production

# Or via Helm
helm upgrade --install aisensoredgecomp ./helm/aisensoredgecomp \
  --values ./helm/values-production.yaml \
  --values ./sectors/oil-gas/values-overrides.yaml \
  --namespace production
```

## Adding a new sector

1. Copy `sectors/_template/` (TBD) to `sectors/your-sector/`
2. Edit `config.yaml` with sector-specific sensors, compliance, ROI
3. Add `values-overrides.yaml` for Helm
4. Add sector-specific Grafana dashboards in `dashboards/`
5. Add sector-specific tests in `tests/test_matrix.py` (SECTOR-XXX-NNN)
