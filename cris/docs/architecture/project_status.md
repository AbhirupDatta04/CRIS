# Project Status

## CRIS (Credit Risk Intelligence System)

Current state:
- End-to-end lakehouse pipeline (Bronze → Silver → Gold) implemented and validated
- Gold layer enhanced with 30-day behavioural credit risk aggregates
- Feature engineering layer producing model-ready account-level features
- Rule-based default label generation completed for PD modelling
- Baseline Probability of Default (PD) model trained and evaluated (ROC-AUC, KS)
- CI pipeline extended to support phased data contract and risk sanity checks

Next steps:
- Incremental hardening of CI contract and model tests
- Orchestration of pipeline stages using Airflow DAGs
- Iterative feature enrichment and model validation improvements

This file acts as a lightweight status marker reflecting ongoing development.
