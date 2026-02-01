"""
validation_rules.py

Defines atomic validation rules for model outputs.
Each rule checks a single invariant and returns
a count of violations.

This file contains NO execution logic and NO reporting.
"""

import numpy as np
import pandas as pd


def check_pd_column_exists(df: pd.DataFrame, pd_col: str) -> int:
    """
    Rule: PD column must exist in model output.
    """
    return 0 if pd_col in df.columns else -1


def check_pd_nulls(df: pd.DataFrame, pd_col: str) -> int:
    """
    Rule: PD values must not be NULL.
    """
    return df[pd_col].isnull().sum()


def check_pd_nan_or_inf(df: pd.DataFrame, pd_col: str) -> int:
    """
    Rule: PD values must not be NaN or infinite.
    """
    return np.isinf(df[pd_col]).sum() + np.isnan(df[pd_col]).sum()


def check_pd_lower_bound(df: pd.DataFrame, pd_col: str) -> int:
    """
    Rule: PD must be >= 0.
    """
    return (df[pd_col] < 0).sum()


def check_pd_upper_bound(df: pd.DataFrame, pd_col: str) -> int:
    """
    Rule: PD must be <= 1.
    """
    return (df[pd_col] > 1).sum()
