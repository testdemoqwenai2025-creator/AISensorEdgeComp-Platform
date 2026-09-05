# AISensorEdgeComp — Platform

> Production-grade scaffold for a planetary-scale IoT + edge AI platform.
> FastAPI + MQTT + Kafka + TimescaleDB + Flink + Iceberg + ClickHouse + Kubernetes.

This repository contains the **deployable reference implementation** of the
AISensorEdgeComp platform. It is the engineering artifact that backs the
[investor preview](https://testdemoqwenai2025-creator.github.io/DemoSentinelEdge/)
and the [live MVP dashboard](https://preview-chat-beeb4b2b-e7e5-4b02-a2cd-72b95656e3a8.space-z.ai/).

## Repository structure

```
AISensorEdgeComp-Platform/
├── services/                # Microservices
│   ├── ingest/               # MQTT subscriber + Kafka producer (FastAPI)
│   ├── stream/               # Flink jobs for stream processing
│   ├── storage/              # TimescaleDB + Iceberg + ClickHouse writers
│   ├── api/                  # REST + GraphQL API for queries
│   └── ml/                   # ML inference service (TS-FM + RUL)
├── schemas/                  # Data contracts
│   ├── avro/                 # Avro schemas (.avsc) for Kafka topics
│   └── proto/                # Protobuf schemas (.proto) for gRPC + storage
├── k8s/                      # Kubernetes manifests (per environment)
├── helm/                     # Helm charts for production deploy
├── ml/
│   ├── training/             # TS-FM training pipeline
│   ├── inference/            # Real-time inference server
│   └── monitoring/            # Model drift + performance monitoring
├── sectors/                  # Sector-specific configs + reference architectures
│   ├── oil-gas/
│   ├── chemical-plant/
│   ├── hospital-icu/
│   ├── autonomous-vehicles/
│   ├── smart-grid/
│   ├── mining/
│   └── water-treatment/
├── datasets/                # 🆕 Synthetic dataset for researchers + benchmarking
│   ├── synthetic-industrial-telemetry-v1.parquet  # 1M rows, 36MB, Apache 2.0
│   ├── README.md            # Kaggle-style docs with quick-start code
│   ├── CITATION.bib          # Academic citation
│   └── LICENSE
├── tests/                    # 100+ edge-case test scenarios
├── docs/                     # Engineering documentation
└── scripts/                  # Dev + ops scripts
```

## Quick start (local development)

Requirements: Docker 24+, Docker Compose v2, Python 3.12, Bun or Node 20+.

```bash
# 1. Clone
git clone https://github.com/testdemoqwenai2025-creator/AISensorEdgeComp-Platform.git
cd AISensorEdgeComp-Platform

# 2. Copy env
cp .env.example .env

# 3. Start the full stack (Kafka, MQTT broker, TimescaleDB, FastAPI ingest, etc.)
docker compose up -d

# 4. Verify services are healthy
make health

# 5. Send a test telemetry message
make test-telemetry

# 6. Query the API
curl http://localhost:8000/api/v1/sensors | jq
```

## Architecture

```
   Sensors  ──MQTT──►  ingest (FastAPI)  ──Kafka──►  stream (Flink)
                                                          │
                                                          ▼
                                          ┌───────────────┴───────────────┐
                                          ▼                               ▼
                                    TimescaleDB                      Iceberg (S3)
                                    (hot, 30d)                       (cold, forever)
                                          │                               │
                                          └───────────────┬───────────────┘
                                                          ▼
                                                    api (FastAPI)
                                                          │
                                                          ▼
                                                  ClickHouse (OLAP)
```

- **Hot path** (real-time): sensor → MQTT → ingest → Kafka → Flink → TimescaleDB → API
- **Cold path** (batch): Flink → Iceberg (Parquet on S3) → ClickHouse (OLAP queries)
- **ML inference**: Flink emits anomaly tokens → ml service → API exposes predictions

## Production deployment

```bash
# Deploy to k8s (requires kubectl + helm)
make deploy-prod NAMESPACE=production

# Or via Helm directly
helm install aisensoredgecomp ./helm/aisensoredgecomp \
  --values ./helm/values-production.yaml \
  --namespace production
```

## Documentation

- [Architecture deep dive](docs/ARCHITECTURE.md)
- [Data schemas](docs/SCHEMAS.md)
- [ML design](docs/ML_DESIGN.md)
- [Test matrix](docs/TEST_MATRIX.md)
- [Sector configurations](docs/SECTORS.md)
- [Operations runbook](docs/OPERATIONS.md)
- [Security model](docs/SECURITY.md)

## 🆕 Synthetic dataset

We publish a 1M-row synthetic industrial telemetry dataset (36MB Parquet, Apache 2.0)
matching our Avro schema. Designed for researchers benchmarking anomaly detection,
platform engineers testing Kafka/Flink pipelines, and educators teaching industrial IoT.

```bash
# Read with pandas
python -c "import pandas as pd; df = pd.read_parquet('datasets/synthetic-industrial-telemetry-v1.parquet'); print(df.head())"

# Or query with DuckDB
duckdb -c "SELECT sensor_kind, count(*), avg(value) FROM 'datasets/synthetic-industrial-telemetry-v1.parquet' GROUP BY sensor_kind"
```

See [`datasets/README.md`](datasets/README.md) for full docs, quick-start code, and citation info.

## Sector-specific deployments

Each sector has its own config under `sectors/`. See [sectors/README.md](sectors/README.md).

| Sector | Config | Reference arch |
|--------|--------|----------------|
| Oil & Gas | `sectors/oil-gas/` | Upstream + downstream + pipeline |
| Chemical Plant | `sectors/chemical-plant/` | Reactor + distillation + storage |
| Hospital ICU | `sectors/hospital-icu/` | Patient monitoring + clinical alerts |
| Autonomous Vehicles | `sectors/autonomous-vehicles/` | Fleet + perception + safety |
| Smart Grid | `sectors/smart-grid/` | Generation + transmission + distribution |
| Mining | `sectors/mining/` | Surface + underground + processing |
| Water Treatment | `sectors/water-treatment/` | Intake + treatment + distribution |

## License

Apache 2.0 — see [LICENSE](LICENSE).

## Contact

- Engineering: platform@aisensoredgecomp.ai
- Design partners: design@aisensoredgecomp.ai
- Investor relations: partners@aisensoredgecomp.ai

© 2026 AISensorEdgeComp
