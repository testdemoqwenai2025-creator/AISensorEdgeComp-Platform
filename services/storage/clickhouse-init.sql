-- =====================================================================
-- AISensorEdgeComp — ClickHouse OLAP schema
-- =====================================================================

CREATE DATABASE IF NOT EXISTS aisensoredgecomp;
USE aisensoredgecomp;

-- ─── Cold telemetry (archived from Iceberg) ─────────────────────────
CREATE TABLE IF NOT EXISTS telemetry_cold (
    sensor_id       String,
    sensor_kind     LowCardinality(String),
    physical_quantity String,
    unit            LowCardinality(String),
    value           Float64,
    uncertainty     Float64,
    timestamp_ns    UInt64,
    sample_rate_hz  Float64,
    ingested_at     DateTime
) ENGINE = MergeTree
PARTITION BY toYYYYMM(ingested_at)
ORDER BY (sensor_id, ingested_at)
TTL ingested_at + INTERVAL 5 YEAR
SETTINGS index_granularity = 8192;

-- ─── Aggregated anomaly counts (per sensor, per hour) ──────────────
CREATE TABLE IF NOT EXISTS anomaly_counts_hourly (
    sensor_id       String,
    bucket          DateTime,
    anomaly_count   UInt32,
    avg_confidence  Float32,
    max_severity    LowCardinality(String)
) ENGINE = SummingMergeTree
PARTITION BY toYYYYMM(bucket)
ORDER BY (sensor_id, bucket);

-- ─── RUL predictions ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS rul_predictions (
    asset_id        String,
    predicted_at    DateTime,
    rul_hours       Float32,
    confidence      Float32,
    model_version   String,
    features        String  -- JSON
) ENGINE = MergeTree
PARTITION BY toYYYYMM(predicted_at)
ORDER BY (asset_id, predicted_at);

-- ─── Materialized view: aggregate anomalies hourly ─────────────────
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_anomaly_counts_hourly
TO anomaly_counts_hourly AS
SELECT
    sensor_id,
    toStartOfHour(ingested_at) AS bucket,
    countIf(value > 0) AS anomaly_count,
    avg(value) AS avg_confidence,
    'info' AS max_severity
FROM telemetry_cold
WHERE sensor_kind = 'anomaly_score'
GROUP BY sensor_id, bucket;
