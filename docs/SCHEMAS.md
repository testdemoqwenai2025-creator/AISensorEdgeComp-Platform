# Data Schemas

> Avro + Protobuf contracts. See [schemas/](../schemas/) for the files.

## Avro (Kafka wire format)

| Schema | File | Purpose |
|--------|------|---------|
| Telemetry | `schemas/avro/telemetry.avsc` | Canonical measurement (Layer 01 output) |
| Alert | `schemas/avro/alert.avsc` | Alert (Layer 04 output) |
| Asset | `schemas/avro/asset.avsc` | Asset graph node |
| MaintenanceEvent | `schemas/avro/maintenance.avsc` | Maintenance log entry |

## Protobuf (gRPC + storage)

| Schema | File | Purpose |
|--------|------|---------|
| Telemetry | `schemas/proto/telemetry.proto` | Wire format for gRPC + storage |
| Alert | `schemas/proto/alert.proto` | Alert gRPC service |
| Asset | `schemas/proto/asset.proto` | Asset gRPC service |
| MaintenanceEvent | `schemas/proto/maintenance.proto` | Maintenance gRPC service |

## Versioning

- All schemas use `com.aisensoredgecomp.v1` namespace
- Breaking changes require `v2` namespace
- Backward-compatible changes (add optional field, add enum value) in-place
- Schema Registry enforces `BACKWARD` compatibility
- Schema versions registered at deploy time; consumers fall back to latest compatible

## Code generation

```bash
# Avro → Python
python -c "import avro; avro.schema.parse(open('schemas/avro/telemetry.avsc').read())"

# Protobuf → Python
python -m grpc_tools.protoc -I schemas/proto \
  --python_out=./generated --grpc_python_out=./generated \
  schemas/proto/*.proto
```
