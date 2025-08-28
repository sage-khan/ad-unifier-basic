# System and Data Architecture

## Overview

The diagram below gives a conceptual overview of the architecture.

*Sources (APIs/CSV/JSON)*
Google, Meta, etc.
        │
        ▼
*Ingestion (batch or simulate)*
Small Python jobs (per-platform adapters)
        │
        ▼
*Storage & Normalization*
Common schema (date, platform, campaign_id, campaign_name,
impressions, clicks, spend, conversions, revenue) in CSV/Parquet
        │
        ▼
*Analytics*
Pandas/SQL: KPIs (ROAS, CPA, CTR, CVR, CPM), trends, anomaly flags
        │
        ▼
*Serving*
Thin API (FastAPI) + simple UI (Streamlit/Dash) or BI
(Charts, drilldowns, alerts)

_Note: Start with file drops (CSV/JSON); add API adapters later. Common schema enables apples-to-apples KPIs; keep platform-specific fields in a side table for fidelity. Persist columnar (Parquet) once scale grows; enrich with metadata (currency, timezone, attribution window). Alerts: push to Slack/email when anomalies fire; link to pre-filtered dashboard slices._

The following subsection will cover each aspect deeper:

### Data Collection
What we will be doing is to batch connectors to periodically pull raw metrics from Google Ads, Meta, Linkedin, Tiktko (or CSV/JSON for prototyping). Data will be landing raw into a Data Lake (date-partitioned).

### Storage & Normalization
Now we need to Ingest data into a central relational database (e.g., PostgreSQL or SQLite). Normalize by mapping fields (e.g., Google's "cost" to a standard "ad_spend" column) and handling discrepancies like currency or date formats. Data is transformed into a schema: `date, platform, campaign_id, adgroup_id, creative_id, impressions, clicks, spend, conversions, revenue`. Thereon you store in warehouse like Postgres/bigquery with dbt models + tests.

### Semantic Layer & Metrics
We need to define KPIs like ROAS, CPA, CTR, CPM, CVR,CPC once, version controlled. Add “windows” (7/28-day) and cohort dimensions.

### Insights Exposure
Query the database to generate dashboards (e.g., via Streamlit or Tableau embeds) or automated reports. For scalability, add a REST API layer for user queries. Use REST/GraphQL API for dashboards and reports. BI/ Dashboards are for drilldowns. Alerts to be setup on Teams or Slack for anomalies or pacing breaches.

### Smart Features
Smart features can be then included based on the data ops we have setup. Rolling robust z-score on daily platform/campaign metrics, Budget recommendations with guardrails (min spend, min conversions), Chatbot & LLM integration for analysis and predictive modelling.

## Component Sketch (Minimal)

[Sources/APIs or CSV]
      │
      ▼
 [Raw Landing Zone]  ──►  [Canonical Model in Warehouse]
      │                          │
      │                          ├─► [Metrics & Windows (dbt/pandas)]
      │                          ├─► [Anomaly Detector (rolling MAD z-score)]
      │                          └─► [Recommendations Engine]
      ▼
 [Orchestration: cron/Airflow]
      ▼
 [API + Dashboard + Alerts]
