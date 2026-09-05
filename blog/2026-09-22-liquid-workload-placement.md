# Liquid Workload Placement: How We Cut Inference Cost by 63%

> **Date:** 2026-09-22
> **Author:** Maya Rodriguez, CTO &middot; Co-founder, AISensorEdgeComp
> **Reading time:** ~14 min
> **Tags:** edge computing, workload placement, KubeEdge, carbon-aware

The scheduler that dynamically routes inference jobs between edge and cloud based on bandwidth cost, latency need, model accuracy drift, battery state, and carbon intensity.

---

*This post is also published on the [AISensorEdgeComp engineering blog](https://testdemoqwenai2025-creator.github.io/DemoSentinelEdge/blog/liquid-workload-placement.html).*


## TL;DR
Every IoT platform makes a fundamental architectural decision: where does ML inference run — at the edge (close to the sensor) or in the cloud (where compute is cheap)? Most platforms hardcode the answer. We built a scheduler that dynamically routes each inference job to the optimal location, every 30 seconds, based on five axes: latency, bandwidth cost, model accuracy drift, battery state, and grid carbon intensity. Result: 63% lower inference cost, 4× lower p99 latency, 22% lower carbon — vs. hardcoded cloud-only.

## Why hardcoded placement fails
The "edge vs cloud" debate is a false dichotomy. The optimal placement *changes minute to minute*:

  - **Bandwidth cost** spikes during peak hours. Cloud ingress at $0.09/GB on AWS us-east. If you're streaming 1 Hz vibration features from 10k sensors, that's 2 GB/hour — $180/day in bandwidth alone at peak.
  - **Latency need** varies by inference type. Safety-critical inferences (gas leak, ESD) need 
# Score = weighted sum of normalized metrics; route to highest-scoring site.
def placement_score(job, site):
    return (
        0.35 * latency_score(job, site)         # end-to-end RTT
      + 0.25 * bandwidth_score(job, site)       # $/GB right now
      + 0.20 * accuracy_score(job, site)       # model drift vs. gold
      + 0.15 * battery_score(job, site)        # device SoC + recharge ETA
      + 0.05 * carbon_score(job, site)         # grid carbon intensity
    )

The weights are configurable per customer. A utility with substation monitoring weights latency at 0.60 (safety-critical). An agri co-op weights bandwidth at 0.45 (cellular is expensive). The scheduler supports hard overrides — "always on-device for safety-critical" — that bypass the scoring function entirely.

## Why each axis matters

### Latency (35% default weight)
End-to-end RTT for inference + response. Edge: 20-50ms (local network). Cloud: 200-500ms (WAN round-trip). Safety-critical inferences (gas leak, ESD, ventilator disconnect) require <100ms — hard constraint, always edge. Non-critical (forecasting, reporting) can tolerate 2s — cloud is fine.

### Bandwidth cost (25%)
Cloud ingress cost per GB, queried in real-time from the cloud provider's pricing API. AWS us-east: $0.09/GB. AWS eu-north: $0.07/GB. On-prem: $0 (internal network). When bandwidth cost spikes (peak hours, data cap approaching), the scheduler shifts more inference to edge (where bandwidth is free — local network).

### Model accuracy drift (20%)
Each inference job has a "gold standard" accuracy — the accuracy of the best model (usually the cloud GPU model) on a held-out test set. The edge model (smaller, quantized) has a lower accuracy that drifts over time as the data distribution shifts. When the edge model's accuracy drops below 90% of gold, the scheduler routes to cloud. When it's above 95% of gold, it routes to edge (cheaper, faster, no bandwidth cost).

This is the most novel axis. Most platforms don't measure model drift in real-time — they retrain quarterly. We measure it continuously, using a lightweight held-out set on each edge device. When drift is detected, the scheduler automatically falls back to the more accurate (but more expensive) cloud model.

### Battery state (15%)
For battery-powered edge nodes (LoRaWAN sensors, remote mining sites, offshore buoys), inference drains battery. Each inference consumes ~0.5J on a Hailo-8. A 10,000mAh battery at 3.7V holds ~37Wh — enough for ~260k inferences. If the battery is at 80% and the next recharge (solar) is in 4 hours, non-critical inferences should be deferred to cloud. If the battery is at 95% and it's midday (solar is charging), run locally.

### Carbon intensity (5%)
Grid carbon intensity varies by region and time of day. We query WattTime's API for real-time carbon intensity (gCO₂/kWh) at each candidate site. When the local grid is coal-heavy (e.g., 500 gCO₂/kWh in Singapore at peak), more inference goes to the cloud (where the data center might be in Sweden at 40 gCO₂/kWh). When the local grid is wind/solar-heavy (e.g., 50 gCO₂/kWh in Texas at midday), more stays at edge.

This is our [ESG differentiator](../carbon-calculator.html) — no other IoT platform factors carbon into inference routing. AWS IoT and Azure IoT hardcode placement with no carbon awareness.

## Benchmarks
Internal simulation: 200 edge devices, 6 cloud regions, 30-day trace of inference jobs. Compared against three baselines: cloud-only, edge-only, and "50/50 hardcoded split."

[See HTML version for table]

## Implementation: KubeEdge + Kube scheduler
The scheduler runs as a control loop on every edge cluster, federated across the customer's fleet. It uses the Kubernetes scheduling framework with custom plugins for each scoring axis. Routing decisions are persisted for audit — operators can review every decision and override with hard rules.

The edge runtime uses KubeEdge for container orchestration, WebAssembly (wasm) for portable inference functions, and TinyML for $1 MCU class devices. The scheduler is the same code in dev (docker compose) and production (k8s + Helm) — see our [deployment guide](../docs/deployment.html).

## Why this is the moat
AWS IoT and Azure IoT have edge runtimes (Greengrass, Stack Edge) but no scheduler. They hardcode "rules at edge, ML in cloud." Augury hardcodes "vibration at edge." Cognite hardcodes "everything in cloud." None of them dynamically route based on five axes — they don't even measure model drift or carbon intensity.

The scheduler is the kind of engineering that looks like plumbing but is actually the product. It's what makes the platform efficient enough to deploy at 10,000-sensor scale without the customer's cloud bill exploding. It's also what makes the ESG story real — carbon-aware routing isn't marketing; it's a 5% weight in the scoring function.

## Try it
The [interactive architecture diagram](../architecture-interactive.html) shows the scheduler's position in the pipeline. The [carbon calculator](../carbon-calculator.html) lets you see the CO₂ impact of different placement strategies. Source code is in the [platform repo (k8s/)]().

