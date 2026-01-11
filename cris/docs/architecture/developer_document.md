# CRIS — Credit Risk Intelligence System

> **Developer Blueprint & Single Source of Truth**
> Audience: Engineers, reviewers, interviewers, recruiters (technical)
> Purpose: Explain *exactly* what CRIS is, how it works end-to-end, and why each design decision exists — using **banking-aligned concepts**.

---

## 0. What CRIS Is (One-Paragraph Truth)

CRIS (Credit Risk Intelligence System) is a **bank-style credit risk data pipeline** that transforms raw transaction events into **explainable Probability of Default (PD) signals** using SQL-heavy transformations, rule-based labeling, and a baseline Logistic Regression model. The system is intentionally simple, auditable, and interview-defensible, mirroring how **internal risk platforms** in banks are designed rather than how consumer ML demos are built.

This project prioritizes:

* Data lineage over tooling
* Explainability over complex ML
* Banking realism over production-scale infra

---

## 1. Core Banking Concepts Used

CRIS is built around real banking / risk concepts:

* **Account-level modelling** (not transaction-level)
* **Behavioural aggregation windows** (30-day rolling view)
* **Feature stability & interpretability**
* **Rule-based default proxy labels** (early-stage modelling reality)
* **Baseline PD modelling (Logistic Regression)**
* **Metric governance (ROC, KS, sanity checks)**
* **Separation of data layers (Bronze / Silver / Gold)**
* **Orchestration over computation**

These concepts are intentional and interview-aligned.

---

## 2. High-Level System Flow

```
Transaction Events
      ↓
Kafka (simulated ingestion)
      ↓
Bronze Layer (Raw, Immutable)
      ↓
Silver Layer (Cleaned, Standardised)
      ↓
Gold Layer (30-Day Behavioural Aggregates)
      ↓
Feature Engineering (Model-Ready)
      ↓
Label Generation (Default Proxy)
      ↓
PD Model (Logistic Regression)
      ↓
Metrics & Sanity Checks
```

Each arrow represents a **hard contract boundary**.

---

## 3. Ingestion & Bronze Layer

### Purpose (Banking View)

* Preserve **raw truth** of transactions
* Enable replay and audit
* Decouple ingestion from business logic

### Data Characteristics

* One row = one transaction
* Append-only
* No transformations beyond schema enforcement

### Typical Fields

* account_id
* transaction_timestamp
* transaction_amount
* merchant_id
* transaction_type

### What Is *Not* Done Here

* No joins
* No aggregations
* No filters (except schema validity)

> **Why banks do this:** Raw data must always remain accessible for audits, reprocessing, and regulator queries.

---

## 4. Silver Layer — Cleaned Transactions

### Purpose

* Create a **trusted transactional dataset**
* Remove obvious data quality issues

### Transformations Applied

* Filter invalid / null account_ids
* Remove non-positive transaction amounts
* Normalize timestamps
* Cast data types explicitly

### Explicit Non-Goals

* No behavioural logic
* No rolling windows
* No risk indicators

> Silver answers: *“Is this transaction usable?”*
> Gold answers: *“What does this behaviour mean?”*

---

## 5. Gold Layer — Behavioural Aggregation (Core Layer)

### Purpose

* Convert transactions into **credit behaviour signals**
* Provide stable, explainable inputs for risk modelling

### Grain

* One row per account
* Computed over last **30 days**

### Why 30 Days

* Industry-standard short-term behaviour window
* Captures recent stress or inactivity
* Avoids long-term dilution

### Aggregates Produced

| Feature                  | Banking Meaning          |
| ------------------------ | ------------------------ |
| spend_30d                | Total outflow behaviour  |
| txn_count_30d            | Engagement level         |
| avg_amount_30d           | Typical transaction size |
| spend_volatility_30d     | Behaviour instability    |
| merchant_diversity_30d   | Spending spread          |
| recency_days             | Days since last activity |
| low_activity_flag_30d    | Dormancy indicator       |
| high_value_txn_ratio_30d | Large transaction stress |

### SQL Characteristics

* `GROUP BY account_id`
* Time filter: last 30 days
* `SUM`, `COUNT`, `AVG`, `STDDEV`

> **Important:** Banks never model directly on raw transactions.

---

## 6. Feature Engineering Layer

### Purpose

* Convert Gold aggregates into **model-ready features**
* Keep ML code clean and dumb

### Features Created

* spend_per_txn_30d = spend_30d / txn_count_30d
* txn_count_30d (passed through)
* recency_days_is_inactive_30d (binary)

### Design Rules

* Derived strictly from Gold
* No joins
* No time leakage
* No business rules inside model code

> Feature engineering is treated as **data engineering**, not ML magic.

---

## 7. Label Generation — Default Proxy

### Why Proxy Labels Are Used

* Real default labels come from downstream systems
* Early-stage models often rely on **rule-based proxies**

### Label Logic

* Based on behavioural stress signals:

  * High volatility
  * Low activity
  * Poor recency

### Controlled Randomness

* Noise injected intentionally
* Prevents deterministic outcomes
* Fixes unrealistically perfect ROC issues

> This mirrors how **early credit experiments** are done internally.

---

## 8. PD Modelling

### Model Choice

* Logistic Regression

### Why Logistic Regression

* Interpretable coefficients
* Regulatory-friendly baseline
* Easy to sanity-check

### Inputs

* account_features_basic
* default_flag

### Metrics Evaluated

* ROC-AUC (~0.95)
* KS Statistic (~0.89)

### Sanity Checks

* Negative intercept (low base default rate)
* Logical coefficient directions

---

## 9. Model Evaluation Philosophy

* Metrics are **observed, not optimised endlessly**
* No auto-retraining loops
* No hyperparameter hunting

> Risk teams care more about **stability and explainability** than squeezing AUC.

---

## 10. CI Pipeline (Engineering Hygiene)

### Purpose

* Protect assumptions
* Catch silent breaks

### What CI Includes

* Unit tests for core logic
* Schema expectation checks
* Model metric sanity thresholds

### What CI Explicitly Avoids

* Spark execution
* Kafka consumption
* Full model training

### Philosophy

* CI validates **logic**, not infrastructure

---

## 11. Orchestration (Planned — Airflow)

### Why Orchestration Is Needed

* Control execution order
* Enforce data dependencies
* Enable reruns

### Planned DAG Scope

```
Gold Ready Check
      ↓
Feature Engineering
      ↓
Label Generation
      ↓
PD Training
      ↓
Model Evaluation
```

### What Airflow Will *Not* Do

* No streaming
* No real-time scoring
* No infrastructure scaling

> Airflow orchestrates **decisions**, not computation.

---

## 12. What CRIS Demonstrates to Interviewers

* Understanding of bank risk pipelines
* Strong SQL & data modelling fundamentals
* Clear separation of concerns
* Explainable ML mindset
* Engineering discipline without overengineering

---

## 13. Known Limitations (Explicit)

* Synthetic / proxy labels
* No regulatory governance
* No production infra

These are **acknowledged, not hidden**.

---

## 14. Final Mental Model

> CRIS is not a toy ML project.
> It is a **scaled-down internal bank risk platform**, built for clarity, reasoning, and defence.

---

**This document is the authoritative technical blueprint for CRIS.**
