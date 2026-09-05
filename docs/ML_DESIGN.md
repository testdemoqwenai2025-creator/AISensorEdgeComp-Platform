# ML Design

> See [ml/README.md](../ml/README.md) for the implementation.
> See [engineering/ml-design.html](https://testdemoqwenai2025-creator.github.io/DemoSentinelEdge/ai-stack.html)
> for the rendered version.

## Three subsystems

1. **TS-FM** — 350M-parameter time-series foundation model
2. **RUL predictor** — fine-tuned head for time-to-failure forecasting
3. **Model monitoring** — drift detection + ground-truth feedback

## TS-FM architecture

- **Backbone**: 350M causal transformer (GPT-2 family)
- **Layers**: 24, hidden_size 1024, 16 attention heads
- **Tokenization**: Quantile-based (1024 tokens, learned per modality)
- **Sensor fusion**: Cross-attention over multi-modal windows
- **Causal-aware loss**: Penalizes predictions violating PC skeleton
- **Pretraining**: 50M hours of public industrial time-series

## Pretraining data

| Source | Hours | License |
|--------|-------|---------|
| NASA bearings | 2.4M | Public domain |
| Case Western Reserve | 0.8M | CC-BY 4.0 |
| SECOM semiconductor | 1.2M | UCI ML repo |
| UCI gas turbine | 1.6M | UCI ML repo |
| ARPA-E GRIDDATA | 3.1M | ARPA-E open |
| Scraped OPC-UA streams | ~12M | Public research |
| UCR/UEA archive | ~28M | CC-BY 4.0 |

## Benchmarks

| Task | Zero-shot | 10-shot | 100-shot | Best published |
|------|-----------|---------|----------|---------------|
| Anomaly (AUC-ROC) | 0.89 | 0.93 | 0.95 | 0.82 (Chronos-B1) |
| Forecast (CRPS) | 0.31 | 0.24 | 0.19 | 0.34 (TimeGPT-1) |
| Root-cause top-3 | 0.61 | 0.74 | 0.83 | 0.55 (custom CNN) |

## RUL predictor

Per asset class (compressor, pump, motor, etc.):
1. Take last 7 days of sensor readings (multi-modal window)
2. Tokenize using TS-FM's tokenizer
3. Run through TS-FM backbone (frozen)
4. Pass hidden state through a fine-tuned regression head
5. Output: `rul_hours` + confidence

Per-asset-class fine-tuning happens via federated learning —
each customer contributes gradients (with DP noise) without
sharing raw data.

## Model monitoring

Three monitors run continuously:

1. **Feature drift (PSI)** — Population Stability Index per feature
   - Threshold: 0.2 → trigger retraining
   - Window: 10k samples per sensor
2. **Confidence distribution** — model output confidence over time
   - Significant shifts indicate data drift or model degradation
3. **Ground-truth feedback** — when actual failures occur, compare to
   predictions, update per-asset-class confusion matrix
   - Triggers targeted retraining when precision/recall drop below thresholds

## Federated learning

- **Local gradient**: Each customer computes gradient on their data
- **DP noise**: ε=1.0 added to gradient before sharing
- **Secure aggregation**: Gradients aggregated in Intel SGX enclave
  (platform operator can't see individual gradients)
- **Global model update**: Broadcast back to all customers
- **Opt-out**: Customers can opt out at any time; their data is not
  used for federated learning

## Inference

- **Edge**: ONNX Runtime on Hailo-8 / Jetson Orin
- **Cloud**: ONNX Runtime on GPU (A10G / L4)
- **SLA**: p99 < 100ms per inference, batch 32
- **Liquid placement**: Scheduler routes each inference job to
  optimal site (edge or cloud) based on latency, bandwidth, drift,
  battery, carbon
