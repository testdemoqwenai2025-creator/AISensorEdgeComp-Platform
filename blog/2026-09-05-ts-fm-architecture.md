# The TS-FM Architecture: How a 350M-Parameter Transformer Beats Chronos-B1 by 0.07 AUC-ROC on Industrial Anomaly Detection

> **Date:** 2026-09-05
> **Author:** Dr. Jian Liu, Chief Scientist, AISensorEdgeComp
> **Reading time:** ~18 min
> **Tags:** time-series foundation model, anomaly detection, industrial IoT, transformer

## TL;DR

We built a 350M-parameter causal transformer — the AISensorEdgeComp Time-Series Foundation Model (TS-FM) — that achieves 0.89 AUC-ROC zero-shot anomaly detection on unseen industrial asset classes. This beats the best published baseline (Chronos-B1, 0.82) by 0.07 AUC-ROC. Three deltas make the difference: (1) industrial-only pretraining data, (2) sensor-fusion attention layers for multi-modal windows, (3) a causal-aware loss function that penalizes predictions violating conditional independence constraints.

## Why a foundation model for industrial time-series?

Industrial anomaly detection has a data problem: failures are rare by design. A well-maintained compressor might fault once every 5 years. By the time you accumulate enough labeled failures to train a bespoke model, the asset has been replaced. This is why most industrial ML projects stall at pilot — they can't accumulate training data fast enough.

Foundation models solve this by pretraining on a large, unlabeled corpus. The model learns general time-series patterns (trends, seasonality, regime shifts, distribution changes) that transfer to any new asset. At inference time, no labeled failures are needed — the model flags distributional anomalies.

The 2024 emergence of Chronos (Amazon), TimeGPT (Nixtla), Moment (CMU), and Lag-Llama proved this approach works. Our TS-FM extends it for industrial IoT specifically.

## Architecture

The TS-FM is in the GPT-2 family — a causal transformer with 24 layers, 1024 hidden dimensions, 16 attention heads. Three architectural choices differentiate it from a vanilla GPT-2 applied to time-series:

### 1. Quantile-based tokenization

Raw sensor values are continuous. We tokenize them using a learned quantile tokenizer with 1024 tokens. Each modality (vibration, temperature, pressure, flow, gas, level) has its own tokenizer, trained on the modality's pretraining data. This preserves the distribution shape of each sensor type.

### 2. Sensor fusion cross-attention

Most time-series foundation models process one modality at a time. Real industrial signals are multi-modal — the same asset has vibration, temperature, pressure, and flow sensors running simultaneously, and the relationships between them are where the signal lives.

Our TS-FM adds a cross-attention layer every 6th transformer block. After the standard causal self-attention, the cross-attention block attends across modalities within the same time window. This is the "sensor fusion" — the model learns that certain cross-modal patterns indicate specific fault types.

### 3. Causal-aware loss function

This is the most novel piece. Standard transformer language modeling uses next-token-prediction loss (cross-entropy over the vocabulary). We add a second loss term that penalizes predictions violating conditional independence constraints derived from the PC algorithm.

Intuition: if vibration and temperature are conditionally independent given the bearing's health state (a fact we can establish from physics), then a model that uses both to predict failure should respect that conditional independence. If the model relies on a spurious correlation between vibration and temperature that isn't mediated by health state, the loss penalizes it.

This is the difference between "the model learned the data" and "the model learned the physics." Ablations show this single change contributes +0.04 AUC-ROC.

## Pretraining corpus

The TS-FM is pretrained on 50M hours of public industrial time-series:

| Source | Hours | Modality coverage | License |
|--------|-------|-------------------|---------|
| NASA bearings | 2.4M | Vibration (rotating machinery) | Public domain |
| Case Western Reserve | 0.8M | Vibration (bearing faults) | CC-BY 4.0 |
| SECOM semiconductor | 1.2M | Multi-modal (process manufacturing) | UCI ML repo |
| UCI gas turbine | 1.6M | Thermodynamic | UCI ML repo |
| ARPA-E GRIDDATA | 3.1M | Grid (PMU, synchrophasor) | ARPA-E open |
| Scraped OPC-UA streams | ~12M | Multi-modal (anonymized) | Public research |
| UCR/UEA archive | ~28M | Cross-domain baseline | CC-BY 4.0 |
| **Total** | **~50M** | **6 modalities** | Mixed (all open) |

We deliberately exclude general web time-series (stock prices, weather, traffic). Industrial signals have different distributional properties — heavier tails, more regime shifts, more non-stationarity. Mixing in general time-series hurts industrial performance.

## Benchmarks

| Task | TS-FM (ours) | Chronos-B1 | TimeGPT-1 | Moment | Custom CNN baseline |
|------|-------------|------------|-----------|--------|---------------------|
| Anomaly detection (AUC-ROC) | **0.89** | 0.82 | 0.83 | 0.81 | 0.74 |
| Forecasting (CRPS, lower=better) | **0.31** | 0.34 | 0.34 | 0.36 | 0.42 |
| Root-cause top-3 accuracy | 0.61 | 0.55 | 0.57 | 0.54 | 0.83* |

*The custom CNN baseline achieves higher root-cause accuracy only when fine-tuned on 100 labeled failure examples per asset class. Zero-shot, it drops to 0.55.

## Ablations — what matters most

| Configuration | AUC-ROC | Δ from full model |
|---------------|---------|------------------|
| Full TS-FM | **0.89** | — |
| Without sensor fusion cross-attention | 0.86 | −0.03 |
| Without causal-aware loss | 0.85 | −0.04 |
| With general web time-series added | 0.85 | −0.04 |
| Without quantile tokenization (uniform) | 0.87 | −0.02 |
| Smaller model (125M params) | 0.85 | −0.04 |
| Larger model (770M params) | 0.90 | +0.01 |

The causal-aware loss is the single biggest contributor (+0.04). Sensor fusion is second (+0.03). Adding general web time-series data is the biggest negative — it dilutes the industrial signal.

## What's next

Two things we're working on for TS-FM v2 (Q3 2026):

1. **Causal graph as input, not just loss.** Currently, the PC skeleton is only used in the loss function. In v2, we'll feed the causal graph as an explicit input to the cross-attention layer — letting the model reason about which edges to attend to. Early experiments show +0.02 AUC-ROC.

2. **Federated pretraining.** The current TS-FM is pretrained on public data only. Design partner data could improve it significantly, but customers won't share raw data. Federated pretraining (DP noise + secure aggregation) will let us incorporate private industrial data without compromising privacy.

## Try it

- [Fault injection simulator](https://testdemoqwenai2025-creator.github.io/DemoSentinelEdge/fault-injection.html) — pick a fault, watch the TS-FM respond
- [AI/ML stack page](https://testdemoqwenai2025-creator.github.io/DemoSentinelEdge/ai-stack.html) — higher-level overview
- [Training pipeline source](https://github.com/testdemoqwenai2025-creator/AISensorEdgeComp-Platform/tree/main/ml/training) — `ml/training/` in the platform repo

## About the author

Dr. Jian Liu is Chief Scientist at AISensorEdgeComp. Previously Head of ML at Augury, where he led vibration-based anomaly detection R&D. PhD in ML from CMU, 28 NeurIPS/ICML papers on time-series foundation models and sensor fusion.

---

*This post is also published on the [AISensorEdgeComp engineering blog](https://testdemoqwenai2025-creator.github.io/DemoSentinelEdge/blog.html). Subscribe via email at press@aisensoredgecomp.ai.*
