# AISensorEdgeComp — Architecture

> Full system architecture. See [engineering/system-design.html](https://testdemoqwenai2025-creator.github.io/DemoSentinelEdge/system-design.html)
> for the rendered, navigable version.

## Overview

The platform is a four-layer substrate:

```
Layer 04: Intelligence    (TS-FM + Graph RAG + Causal + LLM Query)
Layer 03: Edge Compute    (KubeEdge + Liquid Placement + TinyML + WASM)
Layer 02: Connectivity     (Protocol-agnostic bridge + LLM-assisted ontology)
Layer 01: Sensing         (Sensor ontology + Self-calibration mesh)
```

## Hot path (real-time)
```
Sensor → MQTT/OPC-UA → ingest (FastAPI) → Kafka → Flink → TimescaleDB → API
                                                ↓
                                          ML inference (anomaly tokens)
                                                ↓
                                          alerts topic
```

## Cold path (batch + OLAP)
```
Flink → Iceberg (Parquet on S3) → ClickHouse → API
```

## Component inventory

| Component | Image / Service | Purpose |
|-----------|-----------------|---------|
| MQTT broker | eclipse-mosquitto | Sensor ingest endpoint |
| Kafka | bitnami/kafka:3.7 (KRaft) | Stream backbone |
| Schema Registry | bitnami/schema-registry | Avro schema validation |
| TimescaleDB | timescale/timescaledb:2.14-pg16 | Hot storage (30 days) |
| Iceberg REST | tabulario/iceberg-rest | Cold storage catalog |
| MinIO | minio/minio | S3-compatible storage (dev) |
| ClickHouse | clickhouse/clickhouse-server:24-alpine | OLAP queries |
| Flink | flink:1.19 | Stream processing + ML inference |
| Ingest | ghcr.io/.../aisensoredgecomp-ingest | MQTT subscriber + Kafka producer |
| API | ghcr.io/.../aisensoredgecomp-api | REST + GraphQL queries |
| ML | ghcr.io/.../aisensoredgecomp-ml | ONNX inference server |
| Prometheus | prom/prometheus | Metrics |
| Grafana | grafana/grafana | Dashboards |

## Sizing (production)

| Component | Replicas | CPU | Memory | Storage |
|-----------|----------|-----|--------|--------|
| Kafka | 5 | 4 | 16Gi | 1Ti / broker |
| Flink TM | 8 | 2 | 4Gi | n/a |
| TimescaleDB | 3 (HA) | 4 | 8Gi | 1Ti |
| ClickHouse | 3 (sharded) | 8 | 16Gi | 5Ti |
| Ingest | 12 | 1 | 1Gi | n/a |
| API | 8 | 2 | 2Gi | n/a |
| ML | 4 (+GPU) | 4 | 8Gi | n/a |

Total cloud footprint: ~120 vCPU, ~256 GiB RAM, ~10 TiB storage.
Sustained throughput: 1M telemetry messages/second, 100B rows cold storage.

## Failure modes

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| MQTT broker down | paho-mqtt reconnect | Automatic reconnect, no message loss |
| Kafka broker down | Strimzi alerts | Consumer rebalance, replicas survive 2-broker loss |
| Flink job fail | Checkpoint + savepoint | Auto-restart from last checkpoint (RTO < 1 min) |
| TimescaleDB down | Patroni + etcd | Automatic failover (RTO < 30s, RPO 0) |
| ClickHouse down | Replica lag alerts | Read from replica, write to surviving shards |
| ML OOM | Liveness probe | Pod restart, model reloads from S3 (<30s) |
| Edge WAN loss | Edge buffer 72h | Edge continues running, resyncs on WAN return |

## Security model

- **TLS everywhere** — all inter-service traffic uses mTLS via Istio
- **Per-customer encryption keys** — KMS-derived, rotated quarterly
- **Per-customer K8s namespaces** — strict RBAC, network policies
- **Federated learning only** — raw data never crosses customer boundaries
- **SOC 2 Type II** in flight (Q1 2027), **ISO 27001** Q2 2027, **IEC 62443** Q3 2027

## Observability

- **Metrics**: Prometheus + Grafana dashboards (per-service, per-customer)
- **Logs**: Loki (structured, queryable via LogQL)
- **Traces**: OpenTelemetry → Jaeger (distributed traces across all services)
- **Alerts**: Alertmanager → PagerDuty + Slack (per-team routing)
- **Audit log**: All admin actions logged with user, timestamp, action, target

## Deployment

- **Local dev**: `docker compose up` (single command, full stack)
- **Production**: Helm chart → Kubernetes (EKS/GKE/AKS or on-prem k8s)
- **Air-gapped**: Same Helm chart, internal image registry, internal S3
