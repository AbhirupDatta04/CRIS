# CRIS – Architecture Summary

CRIS (Credit Risk Intelligence System) is a lakehouse-style credit risk
analytics platform designed to transform raw transactional data into
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
- Behavioural stress indicators implemented as early warning risk signals
- Future default outcomes simulated probabilistically for PD target generation
- Baseline PD model prototyped and evaluated using ROC-AUC and KS metrics
- CI framework established with documented data contract and risk sanity test strategy

## Design Principles
- SQL-first and rule-driven feature logic
- Strong emphasis on explainability and auditability
- Clear separation between behavioural signals and default outcomes
- Clear separation between data engineering and risk modelling concerns
- Architecture aligned with real-world banking risk analytics workflows

This document provides a high-level architectural overview of CRIS
and is intended to evolve only if the system scope is explicitly extended.
