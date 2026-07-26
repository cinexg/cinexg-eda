import os
from typing import Union

import pandas as pd

from .utils import (
    DEFAULT_CORR_THRESHOLD,
    DEFAULT_ID_UNIQUENESS_THRESHOLD,
    DEFAULT_SKEW_THRESHOLD,
    column_type_split,
    iqr_outlier_bounds,
    is_numeric_like,
)


def _load_dataset(data_input: Union[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Internal helper function to load a dataset from a file path or return it if it's already a DataFrame.
    """
    if isinstance(data_input, pd.DataFrame):
        return data_input

    if isinstance(data_input, str):
        if not os.path.exists(data_input):
            raise FileNotFoundError(f"The file '{data_input}' does not exist. Please check the path.")

        file_extension = os.path.splitext(data_input)[1].lower()

        if file_extension == '.csv':
            return pd.read_csv(data_input)
        elif file_extension in ['.xls', '.xlsx']:
            return pd.read_excel(data_input)
        else:
            raise ValueError(f"Unsupported file format '{file_extension}'. Please provide a CSV or Excel file.")

    raise TypeError("Input must be a file path (string) or a pandas DataFrame.")

def analyze(
    data_input: Union[str, pd.DataFrame],
    corr_threshold: float = DEFAULT_CORR_THRESHOLD,
    skew_threshold: float = DEFAULT_SKEW_THRESHOLD,
    id_uniqueness_threshold: float = DEFAULT_ID_UNIQUENESS_THRESHOLD,
) -> dict:
    """
    Perform automatic exploratory data analysis on a dataset.
    """
    df = _load_dataset(data_input)

    # 1. Dataset Overview
    overview = {
        "Rows": df.shape[0],
        "Columns": df.shape[1],
    }

    # 2. Column Type Detection
    split = column_type_split(df)
    numerical_cols = split["numerical"]
    categorical_cols = split["categorical"]
    datetime_cols = split["datetime"]
    boolean_cols = split["boolean"]

    column_types = {
        "Numerical": len(numerical_cols),
        "Categorical": len(categorical_cols),
        "Datetime": len(datetime_cols),
        "Boolean": len(boolean_cols),
        "_num_cols": numerical_cols,
        "_cat_cols": categorical_cols
    }

    # 3. Missing Value Analysis
    missing_percentages = (df.isnull().sum() / len(df)) * 100
    missing_info = missing_percentages[missing_percentages > 0].round(2).to_dict()

    # 4. Statistical Summary (Abbreviated for terminal output, but data is saved)
    stats_summary = {"Numerical": {}, "Categorical": {}, "Boolean": {}, "Datetime": {}}
    for col in numerical_cols:
        col_data = df[col].dropna()
        if not col_data.empty:
            stats_summary["Numerical"][col] = {
                "mean": round(col_data.mean(), 2), "median": round(col_data.median(), 2),
                "std": round(col_data.std(), 2), "min": round(col_data.min(), 2), "max": round(col_data.max(), 2)
            }
    for col in categorical_cols:
        col_data = df[col].dropna()
        if not col_data.empty:
            stats_summary["Categorical"][col] = {
                "unique_values": col_data.nunique(),
                "most_common": col_data.mode().iloc[0] if not col_data.mode().empty else None
            }
    for col in boolean_cols:
        col_data = df[col].dropna()
        if not col_data.empty:
            true_count = int(col_data.sum())
            total = len(col_data)
            stats_summary["Boolean"][col] = {
                "true_count": true_count,
                "false_count": total - true_count,
                "true_ratio": round(true_count / total, 2)
            }
    for col in datetime_cols:
        col_data = df[col].dropna()
        if not col_data.empty:
            stats_summary["Datetime"][col] = {
                "min": str(col_data.min()),
                "max": str(col_data.max()),
                "span_days": (col_data.max() - col_data.min()).days
            }

    # 5. Correlation Analysis
    high_correlations = []
    if len(numerical_cols) > 1:
        corr_matrix = df[numerical_cols].corr()
        # Iterate through the upper triangle of the correlation matrix to avoid duplicates and self-correlation
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                val = corr_matrix.iloc[i, j]
                # Check for strong positive or strong negative correlation
                if abs(val) > corr_threshold:
                    col1, col2 = corr_matrix.columns[i], corr_matrix.columns[j]
                    high_correlations.append({"feature_1": col1, "feature_2": col2, "score": round(val, 2)})

    # 6. Data Quality Checks
    duplicates = int(df.duplicated().sum())
    constant_cols = [col for col in df.columns if df[col].nunique() <= 1]

    skewed_cols = {}
    if numerical_cols:
        skewness = df[numerical_cols].skew()
        # A common rule of thumb: absolute skewness above the threshold means the data is highly skewed
        high_skew = skewness[abs(skewness) > skew_threshold]
        if not high_skew.empty:
            skewed_cols = high_skew.round(2).to_dict()

    # Outliers: IQR rule per numeric column
    outliers = {}
    for col in numerical_cols:
        col_data = df[col].dropna()
        if col_data.empty:
            continue
        lower, upper = iqr_outlier_bounds(col_data)
        count = int(((col_data < lower) | (col_data > upper)).sum())
        if count > 0:
            outliers[col] = {"count": count, "percentage": round(count / len(col_data) * 100, 2)}

    # Likely ID columns: near-unique values across any column type, a common leakage/noise source
    likely_id_cols = [
        col for col in df.columns
        if len(df) > 0 and df[col].nunique() > 1 and df[col].nunique() / len(df) >= id_uniqueness_threshold
    ]

    # Numeric values stored as text: common gotcha when a few stray values force a numeric column to object dtype
    numeric_as_text_cols = [col for col in categorical_cols if is_numeric_like(df[col])]

    quality_checks = {
        "Duplicate_Rows": duplicates,
        "Constant_Columns": constant_cols,
        "Highly_Skewed_Columns": skewed_cols,
        "Outliers": outliers,
        "Likely_ID_Columns": likely_id_cols,
        "Possible_Numeric_As_Text": numeric_as_text_cols,
    }

    ml_suggestions = detect_ml_task(df)

    # Compile the final results dictionary
    results = {
            "Overview": overview,
            "Column_Types": column_types,
            "Missing_Values": missing_info,
            "Statistical_Summary": stats_summary,
            "High_Correlations": high_correlations,
            "Quality_Checks": quality_checks,
            "ML_Suggestions": ml_suggestions
        }

    # --- Terminal Output ---
    print("\n" + "="*30)
    print("🚀 STATLENS REPORT")
    print("="*30)
    print(f"Dataset Shape: {results['Overview']['Rows']:,} Rows x {results['Overview']['Columns']} Columns")

    print("\n⚠️ Data Quality Alerts:")
    if quality_checks["Duplicate_Rows"] > 0:
        print(f"  - Found {quality_checks['Duplicate_Rows']} duplicate rows.")
    if quality_checks["Constant_Columns"]:
        print(f"  - Constant columns (no variance): {', '.join(quality_checks['Constant_Columns'])}")
    if quality_checks["Likely_ID_Columns"]:
        print(f"  - Likely ID columns (near-unique values): {', '.join(quality_checks['Likely_ID_Columns'])}")
    if quality_checks["Possible_Numeric_As_Text"]:
        print(f"  - Numeric-looking values stored as text: {', '.join(quality_checks['Possible_Numeric_As_Text'])}")
    if quality_checks["Outliers"]:
        outlier_summary = ', '.join(f"{col} ({info['count']})" for col, info in quality_checks["Outliers"].items())
        print(f"  - Columns with outliers (IQR rule): {outlier_summary}")
    if (
        not missing_info
        and quality_checks["Duplicate_Rows"] == 0
        and not quality_checks["Constant_Columns"]
        and not quality_checks["Likely_ID_Columns"]
        and not quality_checks["Possible_Numeric_As_Text"]
        and not quality_checks["Outliers"]
    ):
         print("  - Looks clean! No missing values, duplicates, constant columns, or outliers detected.")

    if high_correlations:
        print("\n🔗 Correlation Highlights:")

        for corr in high_correlations:
            relationship = "strongly correlates with" if corr['score'] > 0 else "inversely correlates with"
            print(f"  - {corr['feature_1']} {relationship} {corr['feature_2']} (Score: {corr['score']})")

    print("\n🤖 Machine Learning Suggestions:")
    print(f"  - Guessed Target Column: '{ml_suggestions['Target_Column_Guess']}'")
    print(f"  - Probable ML Task: {ml_suggestions['Task']}")
    print(f"  - Suggested Baseline Models: {', '.join(ml_suggestions['Suggested_Models'])}")
    print(f"  - Reasoning: {ml_suggestions['Reasoning']}")
    print("="*30 + "\n")

    return results

def detect_ml_task(dataframe: pd.DataFrame) -> dict:
    """
    Predict likely machine learning task based on dataset characteristics.
    """
    # Common target column names found in datasets
    target_keywords = ['target', 'label', 'class', 'price', 'salary', 'outcome', 'status', 'is_']
    target_col = None
    matched_keyword = None

    # 1. Try to find a target column by name
    for col in dataframe.columns:
        for keyword in target_keywords:
            if keyword in col.lower():
                target_col = col
                matched_keyword = keyword
                break
        if target_col:
            break

    # 2. If no explicit keyword, assume the last column might be the target (standard in many raw datasets)
    if target_col:
        reasoning = (
            f"Column name '{target_col}' contains the keyword '{matched_keyword}', "
            "a common target-column signal."
        )
    else:
        target_col = dataframe.columns[-1]
        reasoning = (
            f"No column name matched common target keywords ({', '.join(target_keywords)}); "
            f"falling back to the last column '{target_col}', a common convention in raw datasets."
        )

    # 3. Determine task based on the target column's characteristics
    unique_vals = dataframe[target_col].nunique()
    is_numeric = pd.api.types.is_numeric_dtype(dataframe[target_col])

    # Rule: If it's numeric and has many unique values, it's likely predicting a continuous number (Regression)
    if is_numeric and unique_vals > 15:
        task = "Regression"
        models = ["Linear Regression", "Random Forest Regressor", "Gradient Boosting"]
    # Rule: If it has fewer unique values (even if numeric, like 0 and 1), it's likely predicting categories (Classification)
    elif unique_vals <= 15:
        task = "Classification"
        models = ["Logistic Regression", "Random Forest Classifier", "Gradient Boosting Classifier"]
    # Fallback
    else:
        task = "Clustering (Unsupervised)"
        models = ["K-Means", "DBSCAN", "Hierarchical Clustering"]
        target_col = "None detected clearly"
        reasoning += (
            " The guessed column didn't clearly fit classification or regression criteria, "
            "so an unsupervised task is suggested instead."
        )

    return {
        "Target_Column_Guess": target_col,
        "Task": task,
        "Suggested_Models": models,
        "Reasoning": reasoning
    }
