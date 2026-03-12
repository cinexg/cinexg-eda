import pytest
import pandas as pd
from cinexg_eda.analyzer import analyze, _load_dataset

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