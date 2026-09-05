# The Sensor Ontology: Turning Bytes into Meaning

> **Date:** 2026-09-29
> **Author:** Dr. Aarav Kapoor, CEO &middot; Co-founder, AISensorEdgeComp
> **Reading time:** ~12 min
> **Tags:** sensor ontology, semantic normalization, LLM, industrial IoT

Why we built a canonical schema for industrial measurements, how LLM-assisted semantic normalization cuts new-factory onboarding from 6 months to 3 weeks, and why the 6-month number was the hardest thing we ever automated.

---

*This post is also published on the [AISensorEdgeComp engineering blog](https://testdemoqwenai2025-creator.github.io/DemoSentinelEdge/blog/sensor-ontology.html).*


## TL;DR
Every factory floor runs Modbus, OPC-UA, Profinet, MQTT, and proprietary serial — all at once. Bridging them with semantic understanding (not just byte translation) used to take 30-person SI teams 6 months per site. We automated it with an LLM-assisted semantic normalization pipeline that cuts onboarding to 3 weeks. This post explains the canonical schema, the LLM mapping approach, and the audit trail that makes it safe for industrial buyers.

## The $1.2M problem
Before any AI can run, you need to know what your sensors are measuring. This sounds trivial — until you try to do it at a real factory.

A typical oil & gas platform has 10,000+ sensor tags across 6+ protocols. Each tag has a name like `ns=2;s=Line3.CompressorA.OutletPressure` (OPC-UA) or register `40001` (Modbus) or topic `plant_a/line3/compressor_a/vibration` (MQTT). These names mean nothing to an AI model. The model needs to know: this is compressor outlet pressure, measured in Pa, sampled at 1 Hz, with ±120 Pa uncertainty, calibration age 42 days.

Today, this mapping is done manually. A 30-person system integrator team spends 6 months mapping tags at each new site. Cost: $400k-$1.2M per factory. The mapping tables are brittle — any change in the underlying PLC tags breaks downstream analytics. And the work is duplicated at every site — no two factories use the same tag naming convention.

This is the $1.2M problem: the cost of turning raw bytes into meaning, before any AI can run. It's the reason most industrial AI projects stall at pilot — they can't afford to onboard the second factory.

## The canonical schema
We solved this with a canonical measurement schema — a single JSON record that every sensor reading normalizes to, regardless of its source protocol:

{{
  "measurement_id": "meas_01H8X3F…",
  "sensor_id": "sen_press_a3_line3",
  "sensor_kind": "pressure",
  "physical_quantity": "compressor_outlet_pressure",
  "unit": "Pa",
  "value": 182450.0,
  "uncertainty": ±120.0,
  "timestamp_ns": 1788561600000000000,
  "lineage": {{
    "ingest_protocol": "opcua",
    "source_node_id": "ns=2;s=Line3.CompressorA.OutletPressure",
    "calibration_age_days": 42
  }},
  "calibration_confidence": 0.97
}}

This schema is published as [Avro]() and [Protobuf](), Apache 2.0, versioned with the Confluent Schema Registry. Every downstream consumer — TS-FM, Graph RAG, LLM query, API — can rely on this contract.

## LLM-assisted semantic normalization
The hard part is going from `ns=2;s=Line3.CompressorA.OutletPressure` to `physical_quantity="compressor_outlet_pressure", unit="Pa"`. This used to require a human engineer who knew the plant. We automated it with a fine-tuned LLM.

The LLM consumes the source's metadata — OPC-UA node descriptions, Modbus register names, MQTT topic strings, engineering units, data types, EU ranges — and proposes a canonical mapping with confidence scores:

{{
  "source_tag": "ns=2;s=Line3.CompressorA.OutletPressure",
  "source_metadata": {{
    "description": "Outlet pressure of Compressor A on Line 3",
    "data_type": "Double",
    "engineering_unit": "Pa"
  }},
  "proposed_mapping": {{
    "sensor_kind": "pressure",
    "physical_quantity": "compressor_outlet_pressure",
    "unit": "Pa",
    "sample_rate_hz": 1.0
  }},
  "confidence": 0.96,
  "requires_human_approval": true
}}

The LLM is fine-tuned on a corpus of OPC-UA information models, Modbus register conventions, and 200+ anonymized customer tag mappings. It runs on the customer's infrastructure — no raw tag metadata leaves the customer boundary. Federated learning only.

## The human-in-the-loop safety net
The LLM **never writes to the live tag mapping without human approval**. Every proposal is logged with full provenance for audit (SOC 2 evidence package included). Engineers approve; the LLM learns from corrections. Over 3 weeks of onboarding, the LLM's confidence improves from 0.7 to 0.95+ as it learns the customer's naming conventions.

This is the audit trail that makes it safe for industrial buyers. Every mapping decision has: who proposed it (LLM), who approved it (engineer), when, and what the alternatives were. If a mapping is later found to be wrong, the audit trail shows exactly when it was introduced and who approved it — no black box.

## Results: 6 months → 3 weeks
Across 7 design-partner deployments, the LLM-assisted normalization cut onboarding time from an industry-typical 6 months to **3 weeks**:

[See HTML version for table]
The cost reduction is proportional: $400k-$1.2M → $15k-$50k (our onboarding fee for design partners, waived during pilot). This is the difference between "AI is a project" and "AI is a line item."

## Why this is the moat
Cognite does manual mapping (well-structured, but manual). AWS IoT and Azure IoT don't do semantic mapping at all — they give you raw bytes and let you figure out what they mean. ThingsBoard is DIY — you build the mapping yourself. We're the only platform that automates the mapping with an LLM, and the only one that does it with a human-in-the-loop audit trail safe enough for industrial compliance.

This is the 6-month → 3-week reduction that makes our ROI calculator work. Without it, the design partner pilot would take 8 months, not 60 days. The sensor ontology is the foundation — everything else (TS-FM, Graph RAG, LLM query) depends on having clean, canonical data.

## Try it
The [sensor types page](../sensor-types.html) shows the canonical schema in action across 12 sensor types. The [schemas documentation](../docs/schemas.html) has the full Avro/Protobuf specs. Source code for the ingest service (including the LLM-assisted normalization pipeline) is in the [platform repo (services/ingest/)]().

