# Operations Runbook

> Common operational tasks + runbooks.

## Daily checks
- [ ] All pods `Running` (no `CrashLoopBackOff`)
- [ ] Kafka lag < 10k messages per consumer group
- [ ] TimescaleDB disk usage < 70%
- [ ] ClickHouse replica lag < 1000 rows
- [ ] ML drift scores < 0.2
- [ ] Alert queue cleared (no stuck alerts)

## Weekly checks
- [ ] Backup restore test (random restore, verify)
- [ ] Federated learning round completed
- [ ] Audit log review
- [ ] Security patch review (CVEs)
- [ ] Model performance regression test

## Incident response

### Kafka lag spike
1. Check `kafka_consumergroups_lag` in Grafana
2. If > 100k, scale ingest pods: `kubectl scale deploy ingest --replicas=24`
3. If still spiking, check Flink for backpressure
4. If Flink backpressure, scale taskmanagers
5. If persistent, failover to DR region

### ML drift alarm
1. Check `ml_drift_score` per sensor in Grafana
2. Identify drifting features
3. Trigger retraining: `python -m ml.training.train_ts_fm --config ml/training/config.yaml`
4. Deploy new model via Helm canary: 10% traffic
5. Monitor precision/recall for 24h
6. Promote to 100% if healthy

### Edge cluster offline
1. Check edge cluster heartbeat (last seen > 5 min = alert)
2. Customer-side network check (WAN outage?)
3. If WAN down, edge continues 72h on local
4. If edge hardware failure, RMA + ship replacement
5. On return, edge resyncs to cloud automatically

### Customer data breach
1. IMMEDIATE: revoke customer's API keys
2. Identify scope (which customers, which data)
3. Notify customer within 24h (regulatory requirement)
4. Forensic audit log review
5. Patch root cause
6. Post-mortem within 7 days
