import os

import pandas as pd
import pytest

from statlens.visualization import generate_visualizations


@pytest.fixture
def dummy_dataframe():
    return pd.DataFrame({
        "A": [1, 2, 3, 4, 5],
        "B": [5, 4, 3, 2, 1],
        "C": ["cat", "dog", "cat", "bird", "dog"],
    })


def test_generate_visualizations_creates_expected_files(tmp_path, dummy_dataframe):
    output_dir = str(tmp_path / "assets")

    paths = generate_visualizations(dummy_dataframe, output_dir=output_dir)

    assert os.path.exists(paths["missing_plot"])
    assert os.path.exists(paths["corr_plot"])
    assert os.path.exists(paths["hist_plot"])


def test_generate_visualizations_skips_correlation_for_single_numeric_column(tmp_path):
    df = pd.DataFrame({"only_numeric": [1, 2, 3, 4, 5]})
    output_dir = str(tmp_path / "assets")

    paths = generate_visualizations(df, output_dir=output_dir)

    assert paths["corr_plot"] is None
    assert paths["hist_plot"] is not None
    assert os.path.exists(paths["missing_plot"])


def test_generate_visualizations_skips_histogram_for_no_numeric_columns(tmp_path):
    df = pd.DataFrame({"only_categorical": ["cat", "dog", "bird"]})
    output_dir = str(tmp_path / "assets")

    paths = generate_visualizations(df, output_dir=output_dir)

    assert paths["corr_plot"] is None
    assert paths["hist_plot"] is None
    assert os.path.exists(paths["missing_plot"])
