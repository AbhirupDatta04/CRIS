# CRIS – Architecture Summary (as of Dec 31)

CRIS (Credit Risk Intelligence System) is designed as a
lakehouse-style risk platform that transforms transactional data
into credit risk–ready datasets.

## Layers
- **Bronze**: Raw transaction events (Kafka ingestion)
- **Silver**: Cleaned, schema-aligned transaction records
- **Gold**: Account-level behavioural aggregates for credit risk
- **Features**: Model-ready variables (planned)
- **Models**: PD estimation and validation (planned)

## Current Status
- Ingestion and lakehouse layers implemented
- Gold layer produces 30-day credit risk aggregates
- Feature engineering and modelling planned next

## Design Focus
- SQL-first logic
- Explainability over complexity
- Aligned with banking risk workflows
