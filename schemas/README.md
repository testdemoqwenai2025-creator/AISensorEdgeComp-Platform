# Data Schemas

The platform uses **Avro** for Kafka wire format (with Schema Registry) and
**Protobuf** for gRPC services + cold storage. Both formats express the
same logical contracts.

## Files

### Avro (Kafka topics)
- `avro/telemetry.avsc` — Canonical telemetry measurement
- `avro/alert.avsc` — Alert produced by the intelligence layer
- `avro/asset.avsc` — Asset in the asset graph
- `avro/maintenance.avsc` — Maintenance event

### Protobuf (gRPC + storage)
- `proto/telemetry.proto` — Telemetry + SensorKind enum
- `proto/alert.proto` — Alert + Severity enum
- `proto/asset.proto` — Asset
- `proto/maintenance.proto` — MaintenanceEvent + EventType enum

## Versioning

All schemas use the `com.aisensoredgecomp.v1` namespace. Breaking changes
require a new namespace (`v2`). Backward-compatible changes (adding optional
fields, adding enum values) can be made in-place.

## Compatibility

Avro schemas are registered with the Confluent Schema Registry in
`BACKWARD` compatibility mode. Consumers can read data produced by
producers using older schema versions, but not vice versa.

## Code generation

```bash
# Avro → Python
pip install avro
python -c "import avro; avro.schema.parse(open('avro/telemetry.avsc').read())"

# Protobuf → Python
pip install grpcio-tools
python -m grpc_tools.protoc -I proto --python_out=./generated --grpc_python_out=./generated proto/*.proto
```
