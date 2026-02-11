# CRIS — Credit Risk Intelligence System

> An industry grade bank-style credit risk data pipeline that transforms transaction behaviour into explainable Probability of Default (PD) signals using SQL-first data engineering and baseline statistical modelling.

---

## 📌 Overview

**CRIS (Credit Risk Intelligence System)** is a structured, end-to-end credit risk pipeline inspired by how **internal risk platforms in banks** are designed. The project focuses on **clarity, traceability, and explainability**, demonstrating how raw transaction data can be systematically converted into behavioural risk indicators and a baseline Probability of Default (PD) estimate.

This repository intentionally prioritises:

* Strong data modelling fundamentals
* SQL-heavy transformations
* Clear separation of concerns
* Risk-oriented system design

It does **not** aim to be production-grade or regulatory-compliant.

---

## 🏗️ High-Level Architecture

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
Feature Engineering
      ↓
Label Generation (Default Proxy)
      ↓
PD Model (Logistic Regression)
      ↓
Metrics & Sanity Checks
```

Each layer has a **single, well-defined responsibility**, mirroring real-world banking data pipelines.

---

## 🧱 Data Layers Explained

### Bronze Layer — Raw Events

* Stores transaction data as-is
* Append-only and immutable
* Acts as an audit and replay layer

### Silver Layer — Cleaned Transactions

* Data quality checks (nulls, invalid values)
* Type casting and timestamp normalization
* No behavioural or risk logic

### Gold Layer — Behavioural Aggregates

* Account-level aggregation over a 30-day window
* Converts transactions into stable behavioural signals
* Designed specifically for credit risk modelling

---

## 📊 Behavioural Risk Features (Gold Layer)

Examples of aggregates produced:

* `spend_30d`
* `txn_count_30d`
* `avg_amount_30d`
* `spend_volatility_30d`
* `merchant_diversity_30d`
* `recency_days`
* `low_activity_flag_30d`
* `high_value_txn_ratio_30d`

These features reflect **engagement, stability, and behavioural stress** at the account level.

---

## 🧠 Feature Engineering

The feature engineering layer prepares **model-ready inputs** derived strictly from Gold aggregates.

Design principles:

* No joins or external data
* No time leakage
* No business logic inside model code

Example derived features:

* Spend per transaction
* Binary inactivity indicators

---

## 🏷️ Default Outcome Simulation

Future default events are generated probabilistically using behavioural
stress indicators to simulate realistic credit deterioration.

This approach:
- Separates behavioural signals from default outcomes
- Avoids label leakage
- Produces non-deterministic, bank-realistic training targets
  

---

## 📈 PD Modelling

* Baseline **Logistic Regression** model
* Chosen for interpretability and stability
* Evaluated using standard risk metrics:

  * ROC-AUC
  * KS Statistic

Model outputs are treated as **risk signals**, not final credit decisions.

---

## 🔄 Orchestration (Airflow)

Airflow is introduced to simulate how enterprise risk pipelines manage execution order and dependencies.

* DAG structure defines logical sequencing across ingestion, feature engineering, and modelling stages
* Current implementation focuses on orchestration design rather than full production execution

This approach mirrors how orchestration is often developed incrementally in real-world systems.
---
## 🧪 Engineering Practices

CRIS follows disciplined engineering practices aligned with data and risk teams:

* Modular pipeline structure with clear ownership per layer
* Deterministic data transformations
* Explicit validation checks at feature level
* Version-controlled code and documentation

Automated CI/CD and large-scale testing are intentionally out of scope for the current stage of the project.


## 📂 Repository Structure

The repository follows a **data-platform-style layout**, separating ingestion, compute, orchestration, and modelling concerns in a way that mirrors real-world banking systems.

```
project-root/
│
├── dags/                     # Airflow DAGs (orchestration only)
├── docs/                     # System & design documentation
├── ingestion/                # Data ingestion layer
│   └── streaming/
│       └── kafka_producers/  # Kafka producers for transaction events
├── spark/                    # Distributed compute layer
│   └── jobs/
│       ├── bronze/           # Raw ingestion jobs
│       ├── silver/           # Cleaning & standardisation jobs
│       ├── gold/             # Behavioural aggregation jobs
│       ├── features/         # Feature engineering jobs
│       └── utilities/        # Shared Spark utilities
├── models/                   # Risk models
│   └── pd/                   # Probability of Default modelling
├── scripts/                  # Thin execution entrypoints (called by Airflow)
├── tests/                    # Unit and contract tests
├── data/                     # Local / simulated storage
├── docker-compose.yml        # Local
```

---

## 📖 Documentation

## 📖 Documentation

Technical documentation is maintained incrementally within the `docs/` directory and covers:

* Data layer responsibilities and schemas
* Feature engineering logic and assumptions
* Validation rules and sanity checks
* Modelling approach and evaluation metrics

The documentation reflects the system as built, rather than an idealised or future-state design.


---

## ⚠️ Limitations & Scope

* Simplified / proxy default labels
* No regulatory governance or approval workflows
* No production-scale infrastructure

These constraints are **intentional and documented**.

---

## ✅ Project Status

* Core pipeline: complete and stable
* Feature engineering: complete
* PD baseline model: implemented and evaluated
* Orchestration: incremental (Airflow DAG skeleton in place)

---

## 📌 Final Note

CRIS is designed to demonstrate **how credit risk systems are structured**, not just how models are trained. The emphasis is on **data lineage, explainability, and disciplined engineering choices**.
