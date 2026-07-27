"""Small, reusable helpers shared by the analysis engine.

Kept separate from analyzer.py so the threshold defaults and column-splitting
logic aren't duplicated across analyze(), report(), and the CLI.
"""

import pandas as pd

DEFAULT_CORR_THRESHOLD = 0.7
DEFAULT_SKEW_THRESHOLD = 1.0
DEFAULT_ID_UNIQUENESS_THRESHOLD = 0.95


def column_type_split(df: pd.DataFrame) -> dict:
    """Split a DataFrame's columns into numerical, categorical, datetime, and boolean groups."""
    return {
        "numerical": df.select_dtypes(include=["number"]).columns.tolist(),
        "categorical": df.select_dtypes(include=["object", "category", "string"]).columns.tolist(),
        "datetime": df.select_dtypes(include=["datetime"]).columns.tolist(),
        "boolean": df.select_dtypes(include=["bool"]).columns.tolist(),
    }


def iqr_outlier_bounds(series: pd.Series) -> tuple:
    """Return the (lower, upper) IQR fences beyond which values are flagged as outliers."""
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr


def is_numeric_like(series: pd.Series, threshold: float = 0.95) -> bool:
    """Check whether a non-numeric series is mostly parseable as numbers.

    Flags columns that likely should have been read as numeric but were forced
    to object dtype by a handful of stray non-numeric values.
    """
    non_null = series.dropna()
    if non_null.empty:
        return False
    parsed = pd.to_numeric(non_null, errors="coerce")
    return parsed.notna().mean() >= threshold


def json_default(value: object) -> object:
    """Fallback encoder for numpy scalar types that json.dumps can't handle natively.

    Shared by the CLI's --json export and report.py's embedded chart-data JSON,
    both of which serialize analyze() results that carry numpy float64/int64
    scalars (e.g. from Series.round().to_dict()).
    """
    if hasattr(value, "item"):
        return value.item()
    return str(value)
