# CRIS-06 – Gold Layer (Credit Risk Aggregates)

## Purpose
The Gold layer converts cleaned Silver transactions into
**account-level behavioural aggregates** used for credit risk analysis
and downstream modelling.

This layer represents the first point where CRIS transitions from
data processing to **credit risk intelligence**.

---

## Input
- Source: Silver transactions
- Data level: Cleaned, event-level records
- Time column: `timestamp` (cast to canonical `event_time` in Gold)

---

## Output
- Dataset: `account_risk_30d`
- Storage: Parquet
- Grain: One row per `account_id`
- Window: Rolling last 30 days

---

## Aggregates Produced
- `spend_30d` – total spend in last 30 days
- `txn_count_30d` – number of transactions
- `avg_amount_30d` – average transaction value
- `spend_volatility_30d` – variability in spend behaviour
- `merchant_diversity_30d` – distinct merchants used
- `recency_days` – days since last transaction

---

## Design Notes
- Only positive transaction amounts are considered
- Aggregates are explainable and audit-friendly
- Gold output is designed for credit risk feature engineering,
  not reporting or dashboards

---

## Next Step
CRIS-07 – Feature Engineering for PD modelling
