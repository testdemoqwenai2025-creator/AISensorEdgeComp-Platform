# Design Partner Postmortem: 3 Farms, 60 Days, +18% Yield

> **Date:** 2026-10-06
> **Author:** Sofia Costa, CRO &middot; Co-founder, AISensorEdgeComp
> **Reading time:** ~10 min
> **Tags:** design partner, agriculture, postmortem, field deployment

A transparent write-up of the agriculture v1 deployment with 3 design-partner farms. What worked, what didn't, what surprised us, and how the lessons are shaping v2.

---

*This post is also published on the [AISensorEdgeComp engineering blog](https://testdemoqwenai2025-creator.github.io/DemoSentinelEdge/blog/design-partner-postmortem.html).*


## TL;DR
We deployed AISensorEdgeComp agriculture v1 with 3 design-partner farms over 60 days. Result: +18% yield, −30% input cost (fertilizer, water, pesticide). This post is a transparent postmortem — what worked, what didn't, what surprised us, and how the lessons are shaping v2. No marketing; just engineering + operations reality.

## The three farms
[See HTML version for table]

## What we deployed
Each farm got:

  - **Soil probes** (NPK + pH + EC + moisture) at 15-min intervals via LoRaWAN — 1 probe per 20 acres
  - **Weather stations** (12 parameters) at 1-min intervals via Modbus
  - **Sentinel-2 satellite imagery** (10m, 5-day revisit) via STAC API — NDVI, NDRE, LAI
  - **Edge cluster** (RPi 5 + Coral) per farm for local inference + 72h WAN-loss autonomy
  - **Cloud control plane** for cross-farm reasoning + LLM-native query
  - **Grafana dashboard** per farm, with vertical-specific KPIs

## What worked

### 1. The +18% yield number is real
We measured yield against each farm's 3-year historical baseline (same fields, same crops, same management practices — the only variable was our platform). Heartland: +21% corn yield. Green Valley: +14% almond yield. Los Pinos: +19% tomato yield. Average: +18%.

The mechanism: Sentinel-2 NDVI + soil probe NPK fusion identified nitrogen deficiency zones 2-3 weeks earlier than visual scouting. Variable-rate fertilizer application, guided by our per-field recommendation layer, applied nitrogen where it was needed — not blanket across the field. Same for irrigation: soil moisture + weather forecast + Sentinel-2 surface temperature fusion predicted water stress 5 days ahead, enabling pre-emptive irrigation instead of reactive.

### 2. The −30% input cost is real
Heartland reduced fertilizer use by 28% (variable-rate vs. blanket). Green Valley reduced water use by 35% (predictive irrigation vs. scheduled). Los Pinos reduced pesticide use by 32% (Sentinel-2 NDRE detected stress before visual symptoms, enabling spot treatment vs. field-wide spraying). Average: −30%.

### 3. The TS-FM caught a soil probe failure we missed
At Green Valley, the TS-FM flagged a soil probe (probe #34, Block 7) as anomalous — NPK readings were suspiciously stable (zero variance over 48 hours). Our initial reaction: false positive. On inspection, the probe's battery had died and it was reporting its last cached value. The TS-FM caught a *sensor failure*, not a field condition. This is the zero-shot value — the model had never seen a "dead battery" pattern in training, but it recognized "zero variance is anomalous."

### 4. The LLM-native query was the hit feature
Farm managers' favorite feature wasn't the dashboard — it was asking questions in natural language: "Why is Block 7 underperforming?" The LLM composed: "Block 7 shows nitrogen deficiency (soil probe N=42 mg/kg, 35% below field average) and water stress (Sentinel-2 NDVI=0.32 vs. 0.48 field average). Recommend: 40 kg/ha urea + 15mm irrigation within 48 hours." The citation chain pointed to specific probe readings + satellite images. Farm managers forwarded these answers to their agronomists — who verified the recommendations and acted on them.

## What didn't work

### 1. Sentinel-2 cloud cover was a bigger problem than expected
Sentinel-2 has a 5-day revisit, but in Iowa in June, cloud cover meant we sometimes went 12-15 days between usable images. The TS-FM's forecasting model degraded during these gaps. Lesson for v2: fuse Sentinel-1 (SAR, cloud-penetrating) with Sentinel-2 for continuous coverage. We're adding this in Q4 2026.

### 2. LoRaWAN range was overestimated
We planned for 5 km LoRaWAN range (line-of-sight). Reality: 2.5-3 km in Iowa (flat terrain, but crop canopy absorbs signal), 1.5-2 km in California (hills, orchards), 1-2 km in Sinaloa (vegetation density). We needed 2x more gateways than planned. Lesson for v2: plan for 2.5 km range, not 5 km. Budget accordingly.

### 3. The Grafana dashboard was too complex for farm managers
Farm managers wanted 3 things: "what's wrong, what should I do, and when." The Grafana dashboard had 14 panels. They used the LLM query layer 10x more than the dashboard. Lesson for v2: simplify the dashboard to 3 panels (alerts, recommendations, map), and make the LLM query the primary interface.

### 4. Edge cluster setup took 3 days per farm, not 1
We estimated 1 day for edge cluster setup (unbox, connect, configure). Reality: 3 days — LoRaWAN gateway configuration, weather station calibration, soil probe depth verification, cellular backhaul testing. Lesson for v2: pre-configure edge clusters at our facility, ship plug-and-play. Target: 30 minutes per farm.

## What surprised us

### The self-calibration mesh worked for soil probes
Soil probes have 30-day calibration intervals — the highest-drift sensor we handle. We expected the self-calibration mesh (physics redundancy + sparse ground truth + GNN) to reduce recalibration cost by 85%. It did — but it also improved accuracy. The mesh detected 3 probes that were drifting (N readings 15% below true value) and corrected them before we had to send a technician. At $140 per site visit, this saved $420 across the 3 farms — small dollars, but proof the concept works in the field.

### Farm managers shared the LLM answers with their agronomists
We expected farm managers to keep the platform to themselves. Instead, they forwarded LLM-generated recommendations to their contracted agronomists — who then verified the recommendations against their own expertise. The agronomists became our biggest advocates: "This is the first AI tool that tells me *why*, not just *what*." The citation chain was the key — agronomists trust recommendations they can verify.

## What's changing in v2

  - **Sentinel-1 + Sentinel-2 fusion** — continuous coverage regardless of cloud
  - **Simplified dashboard** — 3 panels (alerts, recommendations, map) + LLM as primary interface
  - **Pre-configured edge clusters** — 30-minute setup, not 3 days
  - **2.5 km LoRaWAN planning** — 2x more gateways, proper budget
  - **Agronomist portal** — read-only access for contracted agronomists to verify recommendations

## The numbers
[See HTML version for table]

## Want to be a design partner?
We're signing 5 more design partners for agriculture v2 (Q1 2027). 60-day pilot, free, with engineering support. Sign up via our [self-service portal](../portal.html) or email [design@aisensoredgecomp.ai](mailto:design@aisensoredgecomp.ai). We commit to onboarding your sensor estate (up to 50k tags) within 2 weeks.

