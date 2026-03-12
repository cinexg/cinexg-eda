import pandas as pd
import os

def _load_dataset(data_input):
    """
    Internal helper function to load a dataset from a file path or return it if it's already a DataFrame.
    """
    # 1. If the user already passed a Pandas DataFrame, just return it
    if isinstance(data_input, pd.DataFrame):
        return data_input
    
    # 2. If the user passed a string (file path)
    if isinstance(data_input, str):
        if not os.path.exists(data_input):
            raise FileNotFoundError(f"The file '{data_input}' does not exist. Please check the path.")
            
        file_extension = os.path.splitext(data_input)[1].lower()
        
        # Route based on file extension
        if file_extension == '.csv':
            return pd.read_csv(data_input)
        elif file_extension in ['.xls', '.xlsx']:
            return pd.read_excel(data_input)
        else:
            raise ValueError(f"Unsupported file format '{file_extension}'. Please provide a CSV or Excel file.")
    
    # 3. If they passed something totally wrong (like an integer or a list)
    raise TypeError("Input must be a file path (string) or a pandas DataFrame.")

def analyze(data_input):
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
    numerical_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime']).columns.tolist()
    boolean_cols = df.select_dtypes(include=['bool']).columns.tolist()
    
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
    stats_summary = {"Numerical": {}, "Categorical": {}}
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

    # 5. Correlation Analysis (NEW)
    high_correlations = []
    if len(numerical_cols) > 1:
        corr_matrix = df[numerical_cols].corr()
        # Iterate through the upper triangle of the correlation matrix to avoid duplicates and self-correlation
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                val = corr_matrix.iloc[i, j]
                # Check for strong positive (> 0.7) or strong negative (< -0.7) correlation
                if abs(val) > 0.7:
                    col1, col2 = corr_matrix.columns[i], corr_matrix.columns[j]
                    high_correlations.append({"feature_1": col1, "feature_2": col2, "score": round(val, 2)})

    # 6. Data Quality Checks (NEW)
    duplicates = int(df.duplicated().sum())
    constant_cols = [col for col in df.columns if df[col].nunique() <= 1]
    
    skewed_cols = {}
    if numerical_cols:
        skewness = df[numerical_cols].skew()
        # A common rule of thumb: absolute skewness > 1 means the data is highly skewed
        high_skew = skewness[abs(skewness) > 1]
        if not high_skew.empty:
            skewed_cols = high_skew.round(2).to_dict()
            
    quality_checks = {
        "Duplicate_Rows": duplicates,
        "Constant_Columns": constant_cols,
        "Highly_Skewed_Columns": skewed_cols
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
            "ML_Suggestions": ml_suggestions # Added here
        }
    
    # --- Terminal Output ---
    print("\n" + "="*30)
    print("🚀 CINEXG-EDA REPORT")
    print("="*30)
    print(f"Dataset Shape: {results['Overview']['Rows']:,} Rows x {results['Overview']['Columns']} Columns")
    
    print("\n⚠️ Data Quality Alerts:")
    if quality_checks["Duplicate_Rows"] > 0:
        print(f"  - Found {quality_checks['Duplicate_Rows']} duplicate rows.")
    if quality_checks["Constant_Columns"]:
        print(f"  - Constant columns (no variance): {', '.join(quality_checks['Constant_Columns'])}")
    if not missing_info and quality_checks["Duplicate_Rows"] == 0 and not quality_checks["Constant_Columns"]:
         print("  - Looks clean! No missing values, duplicates, or constant columns.")
         
    if high_correlations:
        print("\n🔗 Correlation Highlights (> 0.7):")
        
        for corr in high_correlations:
            relationship = "strongly correlates with" if corr['score'] > 0 else "inversely correlates with"
            print(f"  - {corr['feature_1']} {relationship} {corr['feature_2']} (Score: {corr['score']})")

    # Add this to the very bottom of your terminal output prints:
    print("\n🤖 Machine Learning Suggestions:")
    print(f"  - Guessed Target Column: '{ml_suggestions['Target_Column_Guess']}'")
    print(f"  - Probable ML Task: {ml_suggestions['Task']}")
    print(f"  - Suggested Baseline Models: {', '.join(ml_suggestions['Suggested_Models'])}")
    print("="*30 + "\n")

    return results
    
def detect_ml_task(dataframe):
    """
    Predict likely machine learning task based on dataset characteristics.
    """
    # Common target column names found in datasets
    target_keywords = ['target', 'label', 'class', 'price', 'salary', 'outcome', 'status', 'is_']
    target_col = None
    
    # 1. Try to find a target column by name
    for col in dataframe.columns:
        if any(keyword in col.lower() for keyword in target_keywords):
            target_col = col
            break
            
    # 2. If no explicit keyword, assume the last column might be the target (standard in many raw datasets)
    if not target_col:
        target_col = dataframe.columns[-1]
        
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
        
    return {
        "Target_Column_Guess": target_col,
        "Task": task,
        "Suggested_Models": models
    }