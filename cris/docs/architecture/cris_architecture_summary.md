# CRIS – Architecture Summary

CRIS (Credit Risk Intelligence System) is a lakehouse-style credit risk
platform designed to transform raw transactional data into
explainable, model-ready datasets for Probability of Default (PD)
modelling.

## Architecture Layers
- **Bronze**: Raw transactional events ingested via Kafka
- **Silver**: Cleaned and schema-aligned transaction records
- **Gold**: Account-level behavioural aggregates over rolling 30-day windows
- **Features**: Interpretable, model-ready behavioural risk variables
- **Models**: Baseline PD estimation and evaluation

## Current Status
- End-to-end Bronze → Silver → Gold pipeline implemented and validated
- Gold layer enhanced with multiple 30-day behavioural risk signals
- Feature engineering layer producing account-level risk features
- Rule-based default label generation implemented for PD modelling
- Baseline PD model trained and evaluated using ROC-AUC and KS metrics
- CI pipeline extended with phased data contract and risk sanity checks

## Design Principles
- SQL-first and rule-driven feature logic
- Strong emphasis on explainability and auditability
- Clear separation between data engineering and risk modelling concerns
- Architecture aligned with real-world banking risk analytics workflows

This document provides a high-level architectural overview of CRIS
and is intended to evolve as the system matures.
