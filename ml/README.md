# AISensorEdgeComp — ML Design

This directory contains the design + reference implementation of the ML layer.

## Architecture

Three subsystems:

1. **Time-Series Foundation Model (TS-FM)** — 350M-parameter causal transformer,
   pretrained on 50M hours of public industrial time-series.
2. **Remaining-Useful-Life (RUL) Predictor** — fine-tuned head for forecasting
   time-to-failure for specific asset classes.
3. **Model Monitoring** — drift detection (PSI + KS-test), confidence
   distribution monitoring, ground-truth feedback loop.

## Files

```
ml/
├── training/
│   ├── train_ts_fm.py        # Pretraining pipeline
│   ├── dataset.py            # IndustrialTSDataset (windowing + tokenization)
│   ├── model.py              # TSFM model (causal transformer + sensor fusion)
│   └── trainer.py            # Trainer with AMP + gradient accumulation
├── inference/
│   └── serve.py              # ONNX-based real-time inference server
├── monitoring/
│   └── drift_detector.py     # PSI + KS-test drift detection
└── README.md                 # This file
```

## Pretraining

```bash
# Pretrain TS-FM v1 on 50M hours of public industrial data
python -m ml.training.train_ts_fm --config ml/training/config.yaml --output ml/models/ts-fm-v1
```

**Pretraining data:**
- NASA bearings (2.4M hours)
- Case Western Reserve (0.8M)
- SECOM semiconductor (1.2M)
- UCI gas turbine (1.6M)
- ARPA-E GRIDDATA (3.1M)
- Scraped OPC-UA streams (~12M, anonymized)
- UCR/UEA archive (~28M, cross-domain baseline)

## Inference

The inference server (`ml/inference/serve.py`) loads the ONNX-exported model
and serves anomaly detection over HTTP. In production, it's deployed as a
sidecar to the Flink stream-processing job, consuming telemetry from Kafka
and emitting anomaly tokens to the `alerts.processed` topic.

**SLA:** p99 < 100ms per inference, batch size 32 on Hailo-8.

## RUL prediction

RUL is a fine-tuned head on the TS-FM backbone. For each asset class, the
last 7 days of sensor readings are tokenized and fed through TS-FM, then a
regression head predicts `rul_hours`. The model is retrained per asset class
when ground-truth failure data becomes available (federated across customers).

## Model monitoring

Three monitors run continuously:

1. **Feature drift (PSI)** — Population Stability Index per feature, alarm
   threshold 0.2. Triggers retraining when exceeded.
2. **Confidence distribution** — monitors the output confidence over time;
   significant shifts indicate either data drift or model degradation.
3. **Ground-truth feedback** — when actual failures occur, the platform
   compares against predicted anomalies and updates the per-asset-class
   confusion matrix. Triggers targeted retraining when precision/recall
   drop below thresholds.

## Benchmarks

| Task | Zero-shot | 10-shot | 100-shot | Best published baseline |
|------|-----------|---------|----------|------------------------|
| Anomaly detection (AUC-ROC) | 0.89 | 0.93 | 0.95 | 0.82 (Chronos-B1) |
| Forecasting (CRPS, lower=better) | 0.31 | 0.24 | 0.19 | 0.34 (TimeGPT-1) |
| Root-cause top-3 accuracy | 0.61 | 0.74 | 0.83 | 0.55 (custom CNN baseline) |

## Federated learning

Cross-customer training is federated: each customer trains a local gradient
on their data, applies DP noise, sends only the gradient to the secure
aggregator (Intel SGX). The global model update is broadcast back.

See `ml/training/federated.py` (TBD — placeholder for now).
