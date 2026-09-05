# Test Matrix

> 100+ edge-case test scenarios. See [tests/matrix.yaml](../tests/matrix.yaml)
> for the full list, and [engineering/test-matrix.html](https://testdemoqwenai2025-creator.github.io/DemoSentinelEdge/)
> for the rendered version.

## Coverage

| Category | Count | Severity breakdown |
|----------|-------|-------------------|
| Ingest (MQTT) | 15 | 9 critical, 5 warning, 1 info |
| Stream (Flink) | 10 | 8 critical, 2 warning |
| Storage (TimescaleDB + Iceberg + ClickHouse) | 12 | 11 critical, 1 warning |
| ML inference | 10 | 7 critical, 3 warning |
| API | 10 | 6 critical, 4 warning |
| Security | 10 | 10 critical |
| Edge cases (weird data) | 10 | 2 critical, 5 warning, 3 info |
| Operational | 10 | 7 critical, 3 warning |
| Compliance | 5 | 5 critical |
| Performance | 8 | 5 critical, 3 warning |
| Multi-tenancy | 4 | 3 critical, 1 warning |
| Schemas (Avro/Protobuf) | 5 | 3 critical, 2 warning |
| Sectors (Oil/Gas/Chem/ICU/AV/Grid/Mine/Water) | 14 | 14 critical |
| Federated learning | 4 | 3 critical, 1 warning |
| Causal inference | 3 | 0 critical, 3 warning |
| **Total** | **130** | (run `pytest tests/test_matrix.py`) |

## Running

```bash
# Run all
pytest tests/test_matrix.py -v

# Run only ingest tests
pytest tests/test_matrix.py -k "INGEST" -v

# Run only critical severity
pytest tests/test_matrix.py -k "critical" -v

# Run only oil-gas sector
pytest tests/test_matrix.py -k "SECTOR-OG" -v
```

## Adding new scenarios

1. Edit `tests/matrix.yaml`
2. Add a new entry under `scenarios:` with a unique ID
3. Specify `input`, `expected`, `severity`
4. Implement the assertion in `tests/test_matrix.py` (route based on ID prefix)
