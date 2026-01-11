"""
CRIS - Credit Risk Intelligence System
Airflow DAG: PD Risk Pipeline Orchestration

Purpose:
- Orchestrate execution order for the CRIS risk pipeline
- Enforce dependencies between Gold → Features → Labels → Model
- No business logic lives here
"""

from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

# -----------------------------
# Task Callables (Wrappers Only)
# -----------------------------

def check_gold_ready(**context):
    """
    Bank-style guardrail:
    - Verify Gold data exists for the process date
    - Fail fast if data is missing

    This task enforces a *data readiness contract*:
    Downstream risk logic must not run unless Gold aggregates
    for the given process_date are present.
    """
    from datetime import date
    import sqlite3

    # In Airflow, execution_date represents the logical run date
    process_date = context.get("ds")  # YYYY-MM-DD

    # NOTE:
    # - SQLite is used here to keep infra simple and local
    # - In real banks, this would be a warehouse (Postgres / Hive / Snowflake)
    conn = sqlite3.connect("/data/cris.db")
    cursor = conn.cursor()

    query = """
        SELECT COUNT(1)
        FROM gold_account_aggregates
        WHERE process_date = ?
    """

    cursor.execute(query, (process_date,))
    row_count = cursor.fetchone()[0]

    conn.close()

    if row_count == 0:
        raise ValueError(
            f"Gold data not available for process_date={process_date}. "
            "Failing pipeline to prevent invalid risk computation."
        )

    print(f"Gold data readiness check passed for process_date={process_date}")


def build_features(**context):
    """
    Trigger feature engineering logic
    """
    print("Building account-level features...")


def generate_labels(**context):
    """
    Trigger rule-based default label generation
    """
    print("Generating default labels...")


def train_pd_model(**context):
    """
    Trigger baseline PD model training
    """
    print("Training PD model (Logistic Regression)...")


def evaluate_model(**context):
    """
    Evaluate model metrics and log results
    """
    print("Evaluating model metrics (ROC, KS)...")


# -----------------------------
# DAG Definition
# -----------------------------

with DAG(
    dag_id="cris_pd_pipeline",
    description="CRIS PD pipeline: Gold → Features → Labels → Model",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    max_active_runs=1,
    tags=["credit-risk", "banking", "pd-model"],
) as dag:

    t1_check_gold = PythonOperator(
        task_id="check_gold_ready",
        python_callable=check_gold_ready,
        provide_context=True,
    )

    t2_build_features = PythonOperator(
        task_id="build_features",
        python_callable=build_features,
        provide_context=True,
    )

    t3_generate_labels = PythonOperator(
        task_id="generate_labels",
        python_callable=generate_labels,
        provide_context=True,
    )

    t4_train_model = PythonOperator(
        task_id="train_pd_model",
        python_callable=train_pd_model,
        provide_context=True,
    )

    t5_evaluate_model = PythonOperator(
        task_id="evaluate_model",
        python_callable=evaluate_model,
        provide_context=True,
    )

    # -----------------------------
    # Dependency Graph
    # -----------------------------

    t1_check_gold >> t2_build_features >> t3_generate_labels >> t4_train_model >> t5_evaluate_model
