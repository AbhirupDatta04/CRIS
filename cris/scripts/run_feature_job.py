"""
CRIS - Feature Engineering Entrypoint

Purpose:
- Acts as a thin execution wrapper for feature generation
- Can be run manually OR triggered by Airflow
- Does NOT contain Spark business logic itself
"""

import argparse
import sys
from datetime import datetime


def run(process_date: str):
    """
    Trigger feature engineering job for a given process date.

    In real execution:
    - This function would call the Spark feature job
    - Here, we keep it explicit and traceable
    """

    print("=" * 60)
    print(f"[CRIS] Starting feature engineering job")
    print(f"[CRIS] Process date: {process_date}")
    print("=" * 60)

    # ---- PLACEHOLDER FOR REAL LOGIC ----
    # Example (later):
    # spark-submit spark/jobs/features/build_features.py --date process_date

    print("[CRIS] Feature engineering completed successfully")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run CRIS feature engineering job")
    parser.add_argument(
        "--date",
        required=True,
        help="Process date in YYYY-MM-DD format",
    )

    args = parser.parse_args()

    try:
        # basic validation
        datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        print("ERROR: --date must be in YYYY-MM-DD format")
        sys.exit(1)

    run(args.date)
