# CRIS – Data Contracts

This document defines the expected data contracts between key layers
in the CRIS (Credit Risk Intelligence System) pipeline. These contracts
ensure downstream stability and prevent silent breakage of risk logic
when upstream transformations change.

## Gold Layer Contract – Account Risk (30D)

**Dataset**: `datalake/gold/account_risk_30d`

### Required Columns
- `account_id` – Unique account identifier
- `spend_30d` – Total spend over the last 30 days
- `txn_count_30d` – Transaction count over the last 30 days
- `avg_amount_30d` – Average transaction amount
- `spend_volatility_30d` – Standard deviation of transaction amounts
- `merchant_diversity_30d` – Count of distinct merchants
- `recency_days` – Days since last transaction
- `low_activity_flag_30d` – Indicator for low engagement
- `high_value_txn_ratio_30d` – Ratio of high-value transactions

### Guarantees
- One row per `account_id`
- Metrics computed over a rolling 30-day window
- No negative monetary values

## Feature Layer Contract – Account Features

**Dataset**: `datalake/features/account_features_basic`

### Required Columns
- `account_id`
- `spend_30d`
- `txn_count_30d`
- `spend_per_txn_30d`
- `recency_days_is_inactive_30d`

### Guarantees
- Feature logic is explainable and deterministic
- No target leakage from model labels

## Model Dataset Contract – PD Training

**Dataset**: `datalake/models/pd_training_dataset`

### Required Columns
- `account_id`
- Feature columns from Feature Layer
- `default_flag` – Binary label used for PD modelling

### Guarantees
- Default rate remains within a realistic range
- Dataset is suitable for baseline PD model training and evaluation

This document is intended to evolve as CRIS matures and additional
validation checks are enforced via CI.