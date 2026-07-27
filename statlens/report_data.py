import random
from datetime import datetime, timezone

import pandas as pd

from .utils import column_type_split

_MAX_NUMERIC_SAMPLES = 2000
_MAX_CATEGORICAL_LABELS = 12


def build_chart_data(df: pd.DataFrame, results: dict, source_label: str) -> dict:
    """
    Build the JSON-serializable dict embedded in the HTML report for its
    client-side interactive charts (correlation heatmap, histograms,
    categorical bars, missingness bars).

    Recomputes a few things analyze() doesn't keep around (the full numeric
    correlation matrix, missingness for every column rather than just the
    >0 subset, capped raw samples for client-side histogram binning) rather
    than widening analyze()'s own return contract.
    """
    from . import __version__

    split = column_type_split(df)
    numerical_cols = split["numerical"]
    categorical_cols = split["categorical"]

    total_rows = len(df)
    missing = {}
    for col in df.columns:
        count = int(df[col].isnull().sum())
        missing[col] = {
            "count": count,
            "percent": round((count / total_rows) * 100, 2) if total_rows else 0.0,
        }

    correlation = {"columns": [], "matrix": []}
    if len(numerical_cols) > 1:
        corr_matrix = df[numerical_cols].corr()
        correlation["columns"] = list(corr_matrix.columns)
        correlation["matrix"] = [
            [None if pd.isna(v) else round(float(v), 4) for v in row]
            for row in corr_matrix.to_numpy()
        ]

    numeric_stats = results["Statistical_Summary"]["Numerical"]
    numeric = {}
    for col in numerical_cols:
        col_data = df[col].dropna()
        if col_data.empty:
            continue
        values = col_data.tolist()
        if len(values) > _MAX_NUMERIC_SAMPLES:
            values = random.sample(values, _MAX_NUMERIC_SAMPLES)
        stats = numeric_stats.get(col, {})
        numeric[col] = {
            "samples": [round(float(v), 6) for v in values],
            "mean": stats.get("mean"),
            "median": stats.get("median"),
            "std": stats.get("std"),
            "min": stats.get("min"),
            "max": stats.get("max"),
        }

    categorical = {}
    for col in categorical_cols:
        col_data = df[col].dropna()
        if col_data.empty:
            continue
        counts = col_data.value_counts()
        top = counts.head(_MAX_CATEGORICAL_LABELS)
        other_count = int(counts.iloc[_MAX_CATEGORICAL_LABELS:].sum())
        categorical[col] = {
            "labels": [str(label) for label in top.index.tolist()],
            "counts": [int(v) for v in top.tolist()],
            "other_count": other_count,
        }

    boolean = {}
    for col, stats in results["Statistical_Summary"].get("Boolean", {}).items():
        boolean[col] = {
            "true_count": stats["true_count"],
            "false_count": stats["false_count"],
        }

    overview = results["Overview"]
    column_types = results["Column_Types"]

    return {
        "meta": {
            "source": source_label,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "version": __version__,
        },
        "overview": {
            "rows": overview["Rows"],
            "columns": overview["Columns"],
            "numerical": column_types["Numerical"],
            "categorical": column_types["Categorical"],
            "datetime": column_types["Datetime"],
            "boolean": column_types["Boolean"],
        },
        "missing": missing,
        "correlation": correlation,
        "numeric": numeric,
        "categorical": categorical,
        "boolean": boolean,
        "quality": results["Quality_Checks"],
        "high_correlations": results["High_Correlations"],
        "ml_suggestions": results["ML_Suggestions"],
    }
