-- =====================================================================
-- AISensorEdgeComp — TimescaleDB schema
-- =====================================================================

CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ─── Canonical measurements (hot, 30-day retention) ─────────────────
CREATE TABLE measurements (
    measurement_id    TEXT PRIMARY KEY,
    sensor_id         TEXT NOT NULL,
    sensor_kind       TEXT NOT NULL,
    physical_quantity TEXT NOT NULL,
    unit              TEXT NOT NULL,
    value             DOUBLE PRECISION NOT NULL,
    uncertainty       DOUBLE PRECISION DEFAULT 0,
    timestamp_ns      BIGINT NOT NULL,
    sample_rate_hz    DOUBLE PRECISION DEFAULT 1.0,
    location          JSONB,
    lineage           JSONB,
    calibration_confidence DOUBLE PRECISION DEFAULT 1.0,
    ingested_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Hypertable partitioned by time
SELECT create_hypertable('measurements', 'ingested_at', chunk_time_interval => INTERVAL '1 day');

-- Indexes for common query patterns
CREATE INDEX idx_measurements_sensor_time ON measurements (sensor_id, ingested_at DESC);
CREATE INDEX idx_measurements_kind_time ON measurements (sensor_kind, ingested_at DESC);
CREATE INDEX idx_measurements_ts ON measurements (timestamp_ns);

-- Retention: 30 days hot, archive to Iceberg via continuous aggregate
SELECT add_retention_policy('measurements', INTERVAL '30 days');

-- ─── Continuous aggregate: 1-minute rollups ─────────────────────────
CREATE MATERIALIZED VIEW measurements_1m
WITH (timescaledb.continuous) AS
SELECT
    sensor_id,
    sensor_kind,
    time_bucket(INTERVAL '1 minute', ingested_at) AS bucket,
    avg(value) AS avg_value,
    min(value) AS min_value,
    max(value) AS max_value,
    count(*) AS sample_count,
    avg(calibration_confidence) AS avg_confidence
FROM measurements
GROUP BY sensor_id, sensor_kind, bucket;

SELECT add_continuous_aggregate_policy('measurements_1m',
    start_offset => INTERVAL '2 hours',
    end_offset   => INTERVAL '5 minutes',
    schedule_interval => INTERVAL '1 minute'
);

-- ─── Assets ─────────────────────────────────────────────────────────
CREATE TABLE assets (
    asset_id      TEXT PRIMARY KEY,
    asset_type    TEXT NOT NULL,
    description   TEXT,
    location      JSONB,
    parent_id     TEXT REFERENCES assets(asset_id),
    metadata      JSONB,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ─── Alerts ─────────────────────────────────────────────────────────
CREATE TABLE alerts (
    alert_id      TEXT PRIMARY KEY,
    sensor_id     TEXT NOT NULL REFERENCES measurements(sensor_id) DEFERRABLE,
    asset_id      TEXT REFERENCES assets(asset_id),
    severity      TEXT NOT NULL CHECK (severity IN ('info', 'warning', 'critical', 'emergency')),
    title         TEXT NOT NULL,
    description   TEXT,
    evidence      JSONB,
    confidence    DOUBLE PRECISION,
    triggered_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    acknowledged_at TIMESTAMPTZ,
    resolved_at   TIMESTAMPTZ
);

CREATE INDEX idx_alerts_severity_time ON alerts (severity, triggered_at DESC);
CREATE INDEX idx_alerts_asset_time ON alerts (asset_id, triggered_at DESC);

-- ─── Maintenance events ─────────────────────────────────────────────
CREATE TABLE maintenance_events (
    event_id      TEXT PRIMARY KEY,
    asset_id      TEXT NOT NULL REFERENCES assets(asset_id),
    event_type    TEXT NOT NULL CHECK (event_type IN ('inspection', 'repair', 'replacement', 'calibration', 'fault')),
    description   TEXT,
    performed_by  TEXT,
    cost_usd      DOUBLE PRECISION,
    started_at    TIMESTAMPTZ NOT NULL,
    completed_at  TIMESTAMPTZ,
    metadata      JSONB
);

CREATE INDEX idx_maintenance_asset_time ON maintenance_events (asset_id, started_at DESC);
