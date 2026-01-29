# CRIS-15: PD Target Semantics Correction & Behavioral Signal Reclassification

## Overview

CRIS-15 addresses a **conceptual modeling issue** identified during PD model development in the Credit Risk Intelligence System (CRIS).

The existing pipeline correctly engineered behavioural features from transaction data but **incorrectly used a behaviour-derived flag as the PD target variable**, leading to label leakage and unrealistic model performance.

This ticket documents the **design correction**, reclassifying behavioural signals as features and redefining Probability of Default (PD) as a **future outcome**, consistent with real-world bank credit risk practices.

---

## Background & Problem Statement

During baseline PD modelling, a rule-based `default_flag` was generated using recent transaction behaviour such as:

- Inactivity
- Low engagement
- High spend per transaction
- Controlled randomness

This flag was subsequently used as the **target variable (`y`)** in the PD model.

While the pipeline executed successfully, this design introduced a **conceptual error**:

- The target variable was directly derived from the same behavioural inputs used as model features
- This resulted in **label leakage**
- Model metrics (ROC-AUC, KS) were unrealistically high and misleading

Such a setup does not represent how PD models operate in real banking environments.

---

## Key Conceptual Correction

### Behavioural Signals vs Default Events

CRIS-15 introduces a clear separation between:

#### Behavioural Stress Indicators
- Derived from recent transaction behaviour
- Represent **current or recent financial stress**
- May or may not result in default
- Valid as **features**, not outcomes

Examples:
- Inactivity flags
- Low transaction frequency
- Large ticket sizes

#### Default Events (PD Target)
- Represent **future observed credit outcomes**
- Occur over a defined horizon (e.g. 6–12 months)
- Are lagged, noisy, and relatively rare
- Serve as the **target variable** for PD modelling

This distinction is fundamental to credit risk modelling in banks.

---

## Changes Introduced in CRIS-15 (So Far)

### 1. Reclassification of Rule-Based Flag

The previously named `default_flag` has been **conceptually reclassified** as:

- `behavioral_stress_flag`

This flag is now treated as:
- A **behavioural feature**
- An early warning / monitoring signal
- An input to PD models, not the PD target itself

No new business logic has been added at this stage.

---

### 2. PD Target Definition Paused Pending Redesign

Since a valid **future default event** is not yet defined in the pipeline:

- Model training scripts expecting a PD target were intentionally allowed to fail
- This prevents accidental training on invalid labels
- CRIS-14 (Model Validation) was paused as validation is meaningless without a correct target

This mirrors real-world bank practice where validation is blocked until model definitions are corrected.

---

### 3. Modular Design Decision

A design decision was made to **separate default-event generation logic** from model training code.

Planned structure (conceptual):

- Training scripts will *consume* a default target
- Default-event logic will live in a **dedicated, reusable module**
- This aligns with model governance and auditability expectations in banks

No implementation has been committed yet.

---

## Why This Change Matters

This correction ensures that CRIS:

- Aligns with real-world PD modelling semantics
- Avoids label leakage and misleading performance metrics
- Reflects proper separation of behaviour, risk signals, and outcomes
- Demonstrates awareness of model risk and governance concerns

Importantly, this change strengthens CRIS as a **learning and interview-ready project**, showing not just implementation skill but **risk modeling judgment**.

---

## Current Status

- Behavioural feature engineering: **Completed**
- Behavioural stress signal: **Correctly classified as feature**
- PD target definition: **Pending redesign**
- Model training: **Temporarily blocked (intentional)**
- CRIS-14 (Model Validation): **Paused**

---

## Related Tickets

- CRIS-08: Feature Engineering (Completed)
- CRIS-11: Baseline PD Modelling (Concept revised)
- CRIS-13: Feature Data Quality & Sanity Checks (Completed)
- CRIS-14: Model Validation & Sanity Checks (Paused)
- **CRIS-15: PD Target Semantics Correction (Active)**

---
---

## Follow-Up Actions (Planned)

- Introduce a dedicated default-event simulation module
- Ensure PD target represents a future observed outcome
- Resume model validation after target correction

(No implementation changes introduced in this ticket.)


## Notes

This ticket documents a **design correction**, not a failure.

Identifying and fixi
