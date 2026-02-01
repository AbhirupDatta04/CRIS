"""
default_event_simulator.py

Simulates observed default events for PD modelling.

This module creates a FUTURE default outcome based on
behavioural stress indicators with probabilistic noise,
to avoid label leakage and deterministic targets.
"""

import numpy as np
import pandas as pd


def generate_observed_default_flag(
    df: pd.DataFrame,
    stress_col: str = "behavioral_stress_flag",
    base_default_rate: float = 0.02,
    stressed_default_rate: float = 0.15,
    random_seed: int = 42
) -> pd.DataFrame:
    """
    Generate a future observed default flag.

    Logic:
    - Non-stressed accounts default with a low base probability
    - Stressed accounts default with a higher probability
    - Many stressed accounts still do NOT default (realistic)

    Returns:
        DataFrame with new column: observed_default_flag
    """

    np.random.seed(random_seed)

    # Sanity check
    if stress_col not in df.columns:
        raise ValueError(f"Required column '{stress_col}' not found in DataFrame")

    random_draw = np.random.rand(len(df))

    df["observed_default_flag"] = np.where(
        df[stress_col] == 1,
        random_draw < stressed_default_rate,
        random_draw < base_default_rate
    ).astype(int)

    return df