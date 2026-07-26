import pytest
import pandas as pd
from statlens.analyzer import analyze, _load_dataset

# 1. We create a "fixture" - a reusable dummy dataset for all our tests
@pytest.fixture
def dummy_dataframe():
    data = {
        "A": [1, 2, 3, 4, 5],
        "B": ["cat", "dog", "cat", "bird", "dog"],
        "C": [10.5, 11.0, None, 12.5, 15.0] # One missing value
    }
    return pd.DataFrame(data)

# 2. Test if our internal loader handles bad inputs correctly
def test_load_dataset_invalid_file():
    # We expect our code to raise a FileNotFoundError if the file doesn't exist
    with pytest.raises(FileNotFoundError):
        _load_dataset("this_file_does_not_exist.csv")

# 3. Test if the main analyze function returns the expected dictionary structure
def test_analyze_structure(dummy_dataframe):
    results = analyze(dummy_dataframe)
    
    # Assertions check if a condition is True. If it's False, the test fails.
    assert isinstance(results, dict), "Analyzer should return a dictionary"
    assert "Overview" in results, "Results missing 'Overview' section"
    assert "Column_Types" in results, "Results missing 'Column_Types' section"
    
# 4. Test if the math is actually correct
def test_analyze_math(dummy_dataframe):
    results = analyze(dummy_dataframe)

    # We know there are 5 rows and 3 columns in our dummy data
    assert results["Overview"]["Rows"] == 5
    assert results["Overview"]["Columns"] == 3

    # We know column C has 1 missing value out of 5 rows (20%)
    assert results["Missing_Values"]["C"] == 20.0


# 5. Outlier detection (IQR rule)
def test_outlier_detection():
    df = pd.DataFrame({"values": [10, 11, 12, 13, 14, 12, 11, 13, 1000]})
    results = analyze(df)

    assert "values" in results["Quality_Checks"]["Outliers"]
    assert results["Quality_Checks"]["Outliers"]["values"]["count"] >= 1


# 6. Likely-ID column detection
def test_likely_id_column_detection():
    df = pd.DataFrame({
        "id": [f"ID{i}" for i in range(20)],
        "category": ["A", "B"] * 10,
    })
    results = analyze(df)

    assert "id" in results["Quality_Checks"]["Likely_ID_Columns"]
    assert "category" not in results["Quality_Checks"]["Likely_ID_Columns"]


# 7. Numeric-looking values stored as text
def test_numeric_as_text_detection():
    df = pd.DataFrame({
        "amount_as_text": ["1", "2", "3", "4", "5"],
        "real_category": ["cat", "dog", "bird", "cat", "dog"],
    })
    results = analyze(df)

    assert "amount_as_text" in results["Quality_Checks"]["Possible_Numeric_As_Text"]
    assert "real_category" not in results["Quality_Checks"]["Possible_Numeric_As_Text"]


# 8. Boolean and datetime columns are actually summarized
def test_boolean_and_datetime_stats():
    df = pd.DataFrame({
        "is_active": [True, True, False, False, True],
        "signup_date": pd.date_range("2023-01-01", periods=5, freq="D"),
    })
    results = analyze(df)

    bool_stats = results["Statistical_Summary"]["Boolean"]["is_active"]
    assert bool_stats["true_count"] == 3
    assert bool_stats["false_count"] == 2
    assert bool_stats["true_ratio"] == 0.6

    date_stats = results["Statistical_Summary"]["Datetime"]["signup_date"]
    assert date_stats["span_days"] == 4


# 9. Configurable thresholds don't change default behavior but do change results when set
def test_id_uniqueness_threshold_is_configurable():
    # 19 unique values out of 20 rows -> ratio 0.95, matching the default threshold exactly
    df = pd.DataFrame({"quasi_id": [f"V{i}" for i in range(19)] + ["V0"]})

    default_results = analyze(df)
    assert "quasi_id" in default_results["Quality_Checks"]["Likely_ID_Columns"]

    strict_results = analyze(df, id_uniqueness_threshold=0.99)
    assert "quasi_id" not in strict_results["Quality_Checks"]["Likely_ID_Columns"]


def test_skew_threshold_is_configurable():
    df = pd.DataFrame({"skewed": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1000]})

    default_results = analyze(df)
    assert "skewed" in default_results["Quality_Checks"]["Highly_Skewed_Columns"]

    lenient_results = analyze(df, skew_threshold=100)
    assert "skewed" not in lenient_results["Quality_Checks"]["Highly_Skewed_Columns"]


def test_corr_threshold_is_configurable():
    # Pearson correlation between these two columns is ~0.853
    df = pd.DataFrame({
        "x": list(range(1, 11)),
        "y": [1, 2, 3, 4, 5, 6, 7, 8, 9, 5],
    })

    default_results = analyze(df)
    pairs = {(c["feature_1"], c["feature_2"]) for c in default_results["High_Correlations"]}
    assert ("x", "y") in pairs

    strict_results = analyze(df, corr_threshold=0.9)
    strict_pairs = {(c["feature_1"], c["feature_2"]) for c in strict_results["High_Correlations"]}
    assert ("x", "y") not in strict_pairs


# 10. ML task reasoning is exposed, not just the guess
def test_ml_reasoning_present(dummy_dataframe):
    results = analyze(dummy_dataframe)

    assert "Reasoning" in results["ML_Suggestions"]
    assert isinstance(results["ML_Suggestions"]["Reasoning"], str)
    assert len(results["ML_Suggestions"]["Reasoning"]) > 0