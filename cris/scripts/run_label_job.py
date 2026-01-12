"""
CRIS - Label Generation Entrypoint

Purpose:
- Acts as a thin execution wrapper for default label generation
- Can be run manually OR triggered by Airflow
- Does NOT contain business logic itself
"""

import argparse
import sys
from datetime import datetime


def run(process_date: str):
    """
    Trigger label generation job for a given process date.

    In real execution:
    - This function would call the label generation logic
    - Keeps orchestration and business logic separated
    """

    print("=" * 60)
    print("[CRIS] Starting default label generation job")
    print(f"[CRIS] Process date: {process_date}")
    print("=" * 60)

    # ---- PLACEHOLDER FOR REAL LOGIC ----
    # Example (later):
    # spark-submit spark/jobs/labels/generate_labels.py --date process_date

    print("[CRIS] Default label generation completed successfully")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run CRIS label generation job")
    parser.add_argument(
        "--date",
        required=True,
        help="Process date in YYYY-MM-DD format",
    )

    args = parser.parse_args()

    try:
        datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        print("ERROR: --date must be in YYYY-MM-DD format")
        sys.exit(1)

    run(args.date)
