# Flink Stream Processing

This directory contains the Flink jobs for real-time stream processing.

## Build

```bash
cd services/stream
sbt assembly
# Output: target/scala-2.12/aisensoredgecomp-stream.jar
```

## Deploy

```bash
# Local (via docker compose)
docker compose up -d flink-jobmanager flink-taskmanager

# Submit job
flink run -m flink-jobmanager:8081 target/scala-2.12/aisensoredgecomp-stream.jar \
  --bootstrap.servers kafka:9092

# Production (via Flink Kubernetes Operator)
kubectl apply -f k8s/flink.yaml
```

## Job: StreamJob

Consumes from `telemetry.raw`, runs `AnomalyDetector` in 30-second windows,
emits to `alerts.processed` and archives to Iceberg.

- **Checkpoint interval**: 60s
- **State backend**: RocksDB
- **Restart strategy**: exponential-delay
- **Parallelism**: 12 (production) / 2 (dev)
- **Exactly-once**: enabled

## Job: AnomalyDetector

Windowed anomaly detection. Loads TS-FM model in `open()`, runs inference
per 30-second window per sensor, emits anomaly tokens when confidence > 0.85.

In production: replace the z-score stub with ONNX Runtime inference of TS-FM.
