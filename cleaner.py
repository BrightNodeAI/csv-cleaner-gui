"""
cleaner.py
Core data cleaning functions for CSV Cleaner GUI.
Used by csv_cleaner_gui.py
"""

import pandas as pd
import numpy as np


# ─────────────────────────────────────────────
#  1. REMOVE DUPLICATES
# ─────────────────────────────────────────────
def remove_duplicates(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Remove duplicate rows. Returns cleaned df and count of removed rows."""
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    return df, removed


# ─────────────────────────────────────────────
#  2. FILL MISSING VALUES
# ─────────────────────────────────────────────
def fill_missing(df: pd.DataFrame, strategy: str = "median", custom_value=None) -> tuple[pd.DataFrame, int]:
    """
    Fill missing values in numeric columns.

    strategy:
        'median'  - fill with column median
        'mean'    - fill with column mean
        'custom'  - fill with custom_value (must be provided)
    """
    total_missing = df.isnull().sum().sum()

    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        if strategy == "median":
            df[col] = df[col].fillna(df[col].median())
        elif strategy == "mean":
            df[col] = df[col].fillna(df[col].mean())
        elif strategy == "custom" and custom_value is not None:
            df[col] = df[col].fillna(custom_value)

    # Fill non-numeric columns with mode or empty string
    non_numeric_cols = df.select_dtypes(exclude=[np.number]).columns
    for col in non_numeric_cols:
        mode = df[col].mode()
        if not mode.empty:
            df[col] = df[col].fillna(mode[0])
        else:
            df[col] = df[col].fillna("")

    return df, int(total_missing)


# ─────────────────────────────────────────────
#  3. HANDLE OUTLIERS  (IQR method)
# ─────────────────────────────────────────────
def handle_outliers(df: pd.DataFrame, method: str = "cap") -> tuple[pd.DataFrame, int]:
    """
    Detect and handle outliers using IQR method.

    method:
        'remove' - drop rows containing outliers
        'cap'    - cap values at IQR boundaries (Winsorize)
        'ignore' - do nothing, return df unchanged
    """
    if method == "ignore":
        return df, 0

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    outlier_count = 0
    rows_to_drop = set()

    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers = df[(df[col] < lower) | (df[col] > upper)]
        outlier_count += len(outliers)

        if method == "remove":
            rows_to_drop.update(outliers.index.tolist())
        elif method == "cap":
            df[col] = df[col].clip(lower=lower, upper=upper)

    if method == "remove" and rows_to_drop:
        df = df.drop(index=list(rows_to_drop)).reset_index(drop=True)

    return df, outlier_count


# ─────────────────────────────────────────────
#  4. FULL CLEAN PIPELINE
# ─────────────────────────────────────────────
def clean_dataframe(
    df: pd.DataFrame,
    fill_strategy: str = "median",
    custom_value=None,
    outlier_method: str = "cap"
) -> tuple[pd.DataFrame, dict]:
    """
    Run the full cleaning pipeline:
    1. Remove duplicates
    2. Fill missing values
    3. Handle outliers

    Returns cleaned DataFrame and a summary dict.
    """
    summary = {}

    df, dupes_removed = remove_duplicates(df)
    summary["duplicates_removed"] = dupes_removed

    df, missing_filled = fill_missing(df, strategy=fill_strategy, custom_value=custom_value)
    summary["missing_filled"] = missing_filled

    df, outliers_handled = handle_outliers(df, method=outlier_method)
    summary["outliers_handled"] = outliers_handled

    return df, summary


# ─────────────────────────────────────────────
#  5. GENERATE REPORT STRING
# ─────────────────────────────────────────────
def build_report(original_df: pd.DataFrame, cleaned_df: pd.DataFrame, summary: dict) -> str:
    """Build a plain-text cleaning report string."""
    lines = [
        "=" * 44,
        "  CSV CLEANER - CLEANING REPORT",
        "=" * 44,
        f"  Original rows    : {len(original_df)}",
        f"  Cleaned rows     : {len(cleaned_df)}",
        f"  Columns          : {len(cleaned_df.columns)}",
        "-" * 44,
        f"  Duplicates removed  : {summary.get('duplicates_removed', 0)}",
        f"  Missing values filled: {summary.get('missing_filled', 0)}",
        f"  Outliers handled    : {summary.get('outliers_handled', 0)}",
        "=" * 44,
    ]
    return "\n".join(lines)
