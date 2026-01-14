# CRIS-13: Feature Data Quality & Sanity Checks

## Overview

CRIS-13 introduces explicit data quality and sanity checks
within the feature engineering layer of the Credit Risk
Intelligence System (CRIS).

The goal is to ensure that all behavioural risk features
used for PD modelling are reliable, logically valid, and
safe to consume by downstream models.

This ticket focuses on **fail-fast guardrails**, not on
feature creation or modelling logic.

---

## Motivation

In credit risk systems, feature integrity is critical.

Invalid, missing, or logically impossible feature values
can silently corrupt model training and evaluation, leading
to misleading risk signals.

CRIS-13 enforces a **feature-level contract** that prevents
bad data from propagating beyond the feature layer.

---

## Scope

### In Scope
- Feature dataset row count validation
- Null-rate checks on critical behavioural features
- Credit-risk sanity bounds on feature values
- Fail-fast behaviour on validation failures

### Out of Scope
- Adding new features
- Modifying existing feature definitions
- Model training or validation
- Airflow orchestration changes
- Statistical drift detection or monitoring

---

## Implemented Checks

All checks are implemented **inside the feature engineering Spark job**
after feature computation and before writing output to the feature layer.

### 1. Row Count Sanity

- Ensures the feature dataset is not empty
- Prevents downstream model execution on zero records

Failure condition:
- Feature row count == 0

---

### 2. Null-Rate Validation

Null-rate thresholds are enforced on the following critical features:

- `spend_30d`
- `txn_count_30d`
- `recency_days_is_inactive_30d`

Rules:
- Null rate per feature must be ≤ 5%
- Threshold is configurable and intentionally conservative

---

### 3. Credit-Risk Value Bounds

The following sanity constraints are enforced:

- `txn_count_30d` must be ≥ 0
- `spend_30d` must be ≥ 0
- `spend_per_txn_30d` must be ≥ 0
- `recency_days_is_inactive_30d` must be binary (0 or 1)

Any violation results in immediate job failure.

---

## Failure Behaviour

If any data quality check fails:
- An exception is raised
- The Spark job terminates
- Downstream pipeline stages are blocked

This ensures invalid feature data does not reach PD modelling.

---

## Design Principles

- Simple, explainable checks
- No statistical assumptions
- No historical baselines required
- Clear error messages for debugging
- Separation of concerns between orchestration and validation

---

## Impact

With CRIS-13 in place:
- Feature outputs are guaranteed to meet basic credit-risk expectations
- Model training and validation can assume clean inputs
- Pipeline failures surface early and transparently

This forms a prerequisite for subsequent model validation work.

---

## Related Tickets

- CRIS-08: Feature Engineering (Completed)
- CRIS-11: Baseline PD Modelling (Completed)
- CRIS-12: Airflow Orchestration (Completed)
- CRIS-14: Model Validation & Sanity Checks (Planned)
