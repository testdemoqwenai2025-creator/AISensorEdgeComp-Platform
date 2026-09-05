# AISensorEdgeComp — Synthetic Industrial Telemetry Dataset v1

> A realistic synthetic industrial telemetry dataset matching the AISensorEdgeComp Avro schema.
> Designed for ML researchers, stream-processing engineers, and platform evaluators.

## Dataset overview

| Field | Value |
|-------|-------|
| **Name** | `synthetic-industrial-telemetry-v1` |
| **Format** | Apache Parquet (zstd compressed) |
| **Rows** | 1,000,000 |
| **File size** | ~25-50 MB (compressed) |
| **Schema** | Matches [`schemas/avro/telemetry.avsc`](../schemas/avro/telemetry.avsc) |
| **License** | Apache 2.0 |
| **Citation** | See [`CITATION.bib`](CITATION.bib) |

## Description

A synthetic industrial telemetry dataset representing 30 days of multi-modal sensor
readings from a hypothetical offshore oil & gas production platform. The data follows
realistic distributions for vibration, temperature, pressure, flow, gas concentration,
and level sensors — including occasional injected anomalies (~0.5% of readings).

The dataset is designed for:
- **ML researchers** benchmarking time-series anomaly detection algorithms
- **Stream-processing engineers** testing Kafka/Flink/Spark pipelines
- **Platform evaluators** validating schema compatibility with their own ingest
- **Educators** teaching industrial IoT concepts with realistic data

## Schema

The Parquet file has these columns (matching `schemas/avro/telemetry.avsc`):

| Column | Type | Description |
|--------|------|-------------|
| `measurement_id` | string | Globally unique ID (ULID-style) |
| `sensor_id` | string | Stable sensor identifier |
| `sensor_kind` | string | One of: vibration, temperature, pressure, flow, gas, level |
| `physical_quantity` | string | e.g., bearing_rms, outlet_temp, outlet_pressure |
| `unit` | string | SI unit, e.g., mm/s RMS, degC, Pa, m3/h, ppm, % |
| `value` | double | The measurement value |
| `uncertainty` | double | ± uncertainty at 1-sigma |
| `timestamp_ns` | int64 | Epoch nanoseconds when measurement was taken |
| `sample_rate_hz` | double | Sample rate in Hz |
| `location_lat` | double | Latitude |
| `location_lon` | double | Longitude |
| `location_elevation_m` | double | Elevation in meters |
| `ingest_protocol` | string | One of: mqtt, opcua, modbus, coap, profinet, ethercat, lorawan, nbiot |
| `source_node_id` | string | OPC-UA-style node ID |
| `ingest_ts` | int64 | Epoch nanoseconds when ingested |
| `calibration_age_days` | int32 | Days since last calibration |
| `calibration_confidence` | double | 0.0-1.0 confidence from self-calibration mesh |

## Sensor catalog (20 sensors)

| Sensor ID | Kind | Quantity | Unit | Baseline | Notes |
|-----------|------|----------|------|----------|-------|
| vib_a3_l3_compressor_a_bearing1 | vibration | bearing_rms | mm/s RMS | 4.5 | Tri-axial MEMS, 10 kHz |
| vib_a3_l3_compressor_a_bearing2 | vibration | bearing_rms | mm/s RMS | 4.3 | Tri-axial MEMS, 10 kHz |
| vib_a3_l3_compressor_b_bearing1 | vibration | bearing_rms | mm/s RMS | 4.6 | Tri-axial MEMS, 10 kHz |
| vib_a3_l3_motor_a_bearing | vibration | bearing_rms | mm/s RMS | 3.8 | Tri-axial MEMS, 10 kHz |
| temp_a3_l3_compressor_a_outlet | temperature | outlet_temp | degC | 72.0 | RTD PT100 |
| temp_a3_l3_compressor_b_outlet | temperature | outlet_temp | degC | 71.5 | RTD PT100 |
| temp_a3_l3_motor_a_winding | temperature | winding_temp | degC | 85.0 | Thermocouple K |
| press_a3_l3_compressor_a_outlet | pressure | outlet_pressure | Pa | 182450 | Piezoresistive |
| press_a3_l3_compressor_b_outlet | pressure | outlet_pressure | Pa | 181800 | Piezoresistive |
| press_a3_l3_separator_inlet | pressure | vessel_pressure | Pa | 850000 | Piezoresistive |
| flow_a3_l3_oil_export | flow | oil_flow | m3/h | 450 | Coriolis |
| flow_a3_l3_gas_export | flow | gas_flow | m3/h | 12500 | Ultrasonic |
| flow_a3_l3_water_injection | flow | water_injection | m3/h | 280 | Magnetic |
| gas_a3_l3_ch4_detector_1 | gas | ch4_concentration | ppm | 5.0 | NDIR infrared |
| gas_a3_l3_h2s_detector_1 | gas | h2s_concentration | ppm | 0.5 | Electrochemical |
| gas_a3_l3_co_detector_1 | gas | co_concentration | ppm | 2.0 | Electrochemical |
| level_a3_l3_separator_oil | level | oil_level_pct | % | 65.0 | Radar FMCW |
| level_a3_l3_separator_water | level | water_level_pct | % | 35.0 | Radar FMCW |
| level_a3_l3_storage_crude | level | crude_level_pct | % | 78.0 | Guided wave |
| level_a3_l3_storage_diesel | level | diesel_level_pct | % | 45.0 | Guided wave |

## Data generation model

Each row is generated using a realistic model:

```python
value = baseline + sine(time, daily_cycle) * 0.5 * variance + gaussian_noise(0, variance * 0.2)
if random() < 0.005:  # 0.5% anomaly injection
    value = baseline ± 3 * variance
```

- **Baseline + daily cycle**: most industrial processes have a 24-hour cycle (ambient temp, demand)
- **Gaussian noise**: realistic sensor noise at 20% of baseline variance
- **Anomaly injection**: 0.5% of readings are 3σ outliers — for testing anomaly detectors
- **Calibration confidence degrades with age**: matches our published self-calibration mesh behavior

## Quick start

### Python (pandas + pyarrow)

```python
import pandas as pd

df = pd.read_parquet("synthetic-industrial-telemetry-v1.parquet")
print(f"Rows: {len(df):,}")
print(df.head())
print(df.describe())

# Filter to vibration anomalies
vib_anomalies = df[
    (df["sensor_kind"] == "vibration") &
    (df["value"] > 8.0)
]
print(f"Vibration anomalies: {len(vib_anomalies):,}")
```

### DuckDB (fast analytical queries)

```sql
INSTALL parquet;
LOAD parquet;

SELECT sensor_kind, count(*), avg(value), stddev(value)
FROM 'synthetic-industrial-telemetry-v1.parquet'
GROUP BY sensor_kind;
```

### Apache Iceberg (for cold storage demos)

```sql
CREATE TABLE telemetry (
    measurement_id STRING,
    sensor_id STRING,
    sensor_kind STRING,
    physical_quantity STRING,
    unit STRING,
    value DOUBLE,
    uncertainty DOUBLE,
    timestamp_ns BIGINT,
    sample_rate_hz DOUBLE,
    location_lat DOUBLE,
    location_lon DOUBLE,
    location_elevation_m DOUBLE,
    ingest_protocol STRING,
    source_node_id STRING,
    ingest_ts BIGINT,
    calibration_age_days INT,
    calibration_confidence DOUBLE
) USING iceberg;
```

### Kafka (for stream processing demos)

```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(bootstrap_servers='localhost:9092')

for row in df.itertuples():
    producer.send('telemetry.raw', json.dumps(row._asdict()).encode('utf-8'))
```

## Reproducibility

The dataset is fully reproducible — it uses `random.seed(42)`. To regenerate
with a different seed or more rows, see
[`scripts/generate_synthetic_dataset.py`](../scripts/generate_synthetic_dataset.py).

## Use cases

### For ML researchers
- Benchmark anomaly detection algorithms (use the 0.5% anomalies as ground truth)
- Test time-series forecasting on a realistic multi-sensor signal
- Validate federated learning approaches (split by sensor_id for federated rounds)

### For platform engineers
- Test Kafka throughput with realistic payload sizes
- Validate Flink windowed aggregation logic
- Test Iceberg/ClickHouse ingest pipelines
- Benchmark schema evolution (add new optional fields, verify backward compat)

### For educators
- Realistic industrial IoT dataset without NDA / privacy concerns
- Multi-modal (6 sensor types) for teaching sensor fusion
- Anomaly labels (via the 3σ rule) for supervised + unsupervised ML teaching

## Comparison to real public datasets

| Dataset | Rows | Modalities | License | Notes |
|---------|------|-----------|---------|-------|
| **NASA bearings** | 2.4M hours | 1 (vibration) | Public domain | Single modality, rotating machinery only |
| **Case Western Reserve** | 0.8M hours | 1 (vibration) | CC-BY 4.0 | Bearing faults, lab-scale |
| **SECOM** | 1.2M hours | ~50 (manufacturing) | UCI ML repo | Multi-sensor, semi-conductor |
| **UCI gas turbine** | 1.6M hours | ~10 | UCI ML repo | Thermodynamic |
| **This dataset** | 1.0M rows | 6 (full industrial) | Apache 2.0 | Schema matches production platform |

## Citation

If you use this dataset in your research, please cite:

```bibtex
@misc{aisensoredgecomp_synthetic_v1,
  title        = {AISensorEdgeComp Synthetic Industrial Telemetry Dataset v1},
  author       = {{AISensorEdgeComp Team}},
  year         = 2026,
  howpublished = {\url{https://github.com/testdemoqwenai2025-creator/AISensorEdgeComp-Platform/tree/main/datasets}},
  note         = {1M rows of synthetic multi-modal industrial telemetry matching the AISensorEdgeComp Avro schema}
}
```

## License

Apache License 2.0 — see [`LICENSE`](LICENSE) and the repo's [LICENSE](../LICENSE) file.

You are free to:
- **Share** — copy and redistribute in any medium
- **Adapt** — remix, transform, and build upon
- **Use commercially** — including in commercial products

Under these terms:
- **Attribution** — cite the dataset (see `CITATION.bib`)
- **No additional restrictions** — don't apply legal terms that restrict others

## Disclaimer

This is **synthetic data**. It does not represent any real-world facility, asset,
or operator. Sensor baselines are chosen to be realistic but do not reflect any
specific industrial process. Use for testing, benchmarking, and education only.
