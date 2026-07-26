# statlens

[![Python package](https://github.com/gauravxsuvo/Statlens/actions/workflows/python-package.yml/badge.svg)](https://github.com/gauravxsuvo/Statlens/actions/workflows/python-package.yml)

statlens is a Python package for automated exploratory data analysis. It takes a
dataset and produces statistical summaries, data quality checks, and a visual report
with minimal code, so you can spend less time on repetitive analysis scripts and more
time interpreting results.

It is intended for developers, data scientists, and students who want a fast first look
at a new dataset before deciding how to clean it or model it.

---

## Features

* Dataset overview: row counts, column counts, and detected data types
* Missing value analysis at the column level
* Statistical summaries: mean, median, min, max, and categorical modes, including
  dedicated summaries for boolean and datetime columns
* Data quality checks for duplicate rows, constant columns, skewed distributions,
  outliers, likely ID columns, and numeric values stored as text
* Correlation analysis that highlights strong relationships between numeric variables
* Automatic suggestions for the likely machine learning task (classification,
  regression, or clustering) based on the dataset's structure, along with the
  reasoning behind the guess
* Visualizations covering correlation matrices, distributions, and missing value
  patterns
* An exportable HTML dashboard containing the full analysis report
* A command line interface and JSON export for use outside a Python script

---

## Installation

Install the package using pip.

```bash
pip install statlens
```

---

## Quickstart

Generate a full exploratory data analysis report in two lines of code.

```python
import statlens

statlens.report("your_dataset.csv", output="eda_report.html")
```

## AI Executive Summary (optional)

statlens can integrate with Google's Gemini to generate a plain-English executive
summary of your dataset, describing likely use cases and calling out data quality
concerns worth investigating.

To enable this feature, you need a free Gemini API key.

1. Get a free API key from Google AI Studio.
2. Set it as an environment variable on your machine.

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

**macOS/Linux:**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

Once the key is set, statlens detects it automatically and adds the AI summary to the
HTML dashboard. If no key is found, this step is skipped and the standard statistical
report is generated on its own, so the package works fully without it.

Your raw data is never sent to the model. Only statistical metadata, such as column
names, missing value percentages, and summary statistics, is transmitted to generate the
summary. Individual rows and values never leave your machine.

The generated HTML dashboard includes:

* dataset statistics
* visualizations
* correlation analysis
* data quality insights

---

## Terminal Summary

If you only want a quick analysis printed to the terminal:

```python
import statlens

results = statlens.analyze("your_dataset.csv")
print(results)
```

This works with CSV files, Excel files, and pandas DataFrames, and returns the same
underlying results dictionary that powers the HTML report.

---

## Command Line Usage

statlens can also be run directly from a terminal, without writing any Python.

```bash
statlens your_dataset.csv
```

This generates `report.html` in the current directory using the same defaults as
`statlens.report(...)`. The command accepts a few options:

```bash
statlens your_dataset.csv --output eda_report.html --json eda_results.json --no-ai
```

* `--output` sets the path for the generated HTML report (default: `report.html`)
* `--json` additionally writes the raw analysis results to a JSON file
* `--no-ai` skips the optional Gemini executive summary, even if `GEMINI_API_KEY`
  is set, which is useful for quick or offline runs

---

## Supported Data Sources

* CSV files
* Excel files
* pandas DataFrames

---

## Technical Requirements

* Python 3.9 or higher
* pandas
* numpy
* matplotlib
* seaborn
* scikit-learn
* google-generativeai (used for the optional AI executive summary)

---

## Project Structure

```
statlens
|
├── statlens
│   ├── __init__.py
│   ├── analyzer.py
│   ├── visualization.py
│   ├── llm_explainer.py
│   ├── report.py
│   ├── cli.py
│   ├── utils.py
│   └── templates
│       └── report_template.html
|
├── tests
│   ├── test_analyzer.py
│   ├── test_visualization.py
│   ├── test_llm_explainer.py
│   └── test_cli.py
|
├── pyproject.toml
└── README.md
```

---

## Roadmap

Planned improvements include:

* automatic feature importance analysis
* dataset drift detection
* interactive web dashboards
* integration with Jupyter notebooks

---

## Contributing

Contributions are welcome. If you would like to improve the package, feel free to open
an issue or submit a pull request.

Steps:

1. Fork the repository
2. Create a new branch
3. Implement your changes
4. Submit a pull request

---

## License

This project is licensed under the MIT License.

---

## Author

Gaurav Raj Singh
GitHub: https://github.com/gauravxsuvo
