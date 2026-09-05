# Security Model

> Threat model + controls. See [engineering/security.html](https://testdemoqwenai2025-creator.github.io/DemoSentinelEdge/)
> for the rendered version.

## Threat model

| Threat | Mitigation |
|--------|-----------|
| Sensor spoofing | Signed measurements + outlier detection in TS-FM |
| Edge device compromise | Full disk encryption (LUKS), signed firmware, TPM 2.0 remote attestation |
| Insider threat | Per-customer key isolation; no employee access to raw sensor data |
| Model exfiltration | Model weights encrypted at rest; inference in SGX / SEV enclaves |
| Pipeline poisoning | All training data has signed provenance; data-source reputation scoring |
| LLM prompt injection | LLM query layer runs with strict output schema validation + citation requirement |

## Compliance posture

| Standard | Status | Target |
|-----------|--------|--------|
| SOC 2 Type II | In progress | Q1 2027 |
| ISO 27001 | Scoping | Q2 2027 |
| IEC 62443 (industrial cybersecurity) | Scoping | Q3 2027 |
| GDPR | Compliant by design | Live at GA |
| HIPAA (health vertical) | Roadmap | 2028 |
| FedRAMP (US gov) | Roadmap | 2028 |

## Customer data isolation

- Per-customer K8s namespace
- Per-customer encryption keys (KMS-derived)
- Per-customer S3 prefix
- Federated learning is the only cross-customer data flow
- Federated learning shares gradients only (with DP noise), never raw data
- SOC 2 audit (in flight) covers this

## Vulnerability disclosure

Email security@aisensoredgecomp.ai. We respond within 24 hours.
PGP key: see [security.txt](https://testdemoqwenai2025-creator.github.io/DemoSentinelEdge/.well-known/security.txt).
