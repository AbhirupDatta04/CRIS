# CRIS-05: Silver Layer Architecture

## Purpose
The Silver layer is responsible for transforming raw/bronze transaction events
into clean, standardized, and analytics-ready records while preserving
event-level granularity.

This layer focuses on data quality and usability, not business insights
or aggregations.

---

## Input
- Source: Bronze transaction dataset (Parquet)
- Characteristics:
  - Event-level records
  - Timestamps stored as strings
  - Possible nulls or duplicate events
  - Includes ingestion metadata (`ingested_at`)

---

## Responsibilities
The Silver layer performs the following transformations:

- Timestamp normalization  
  - Convert event timestamp from string to proper TIMESTAMP (`event_time`)

- Data type enforcement  
  - Financial amounts cast to DECIMAL for precision
  - IDs enforced as numeric types

- Data quality checks  
  - Filter records with missing critical identifiers
  - Ensure basic schema consistency

- Event-level preservation  
  - No aggregations
  - No feature engineering
  - No risk metrics

---

## Output
- Clean, standardized transaction table
- Safe for SQL analytics and downstream processing
- Retains audit and lineage metadata via `ingested_at`

---

## Design Notes
- Silver guarantees correctness and usability, not insights
- Deduplication (if required) is limited to obvious cases
- Business logic and metrics are deferred to the Gold layer
