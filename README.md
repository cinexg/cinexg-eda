# cinexg-eda

[![Python package](https://github.com/cinexg/cinexg-eda/actions/workflows/python-package.yml/badge.svg)](https://github.com/cinexg/cinexg-eda/actions/workflows/python-package.yml)

cinexg-eda is a Python package for automated exploratory data analysis (EDA).
It quickly analyzes datasets and generates clear statistical summaries, data quality checks, and visual reports with minimal code.

The goal is to help developers, data scientists, and students understand datasets instantly without writing repetitive analysis scripts.

---

## Features

* Dataset overview with row counts, column counts, and detected data types
* Missing value analysis with column level statistics
* Statistical summaries including mean, median, min, max, and categorical modes
* Data quality checks for duplicate rows, constant columns, and skewed distributions
* Correlation analysis highlighting strong relationships between variables
* Automatic machine learning task suggestions such as classification, regression, or clustering
* Visualizations including correlation matrices, distributions, and missing value heatmaps
* Exportable HTML dashboard containing the full analysis report

---

## Installation

Install the package using pip.

```bash
pip install cinexg-eda
```

---

## Quickstart

Generate a full exploratory data analysis report in two lines of code.

```python
import cinexg_eda

cinexg_eda.report("your_dataset.csv" , output="eda_report.html")
```

## 🧠 AI Executive Summary (Optional)

`cinexg-eda` integrates with Google's Gemini 2.5 AI to generate a plain-English executive summary of your dataset, explaining potential machine learning use cases and data quality warnings.

To enable this feature, you just need a free Gemini API key:

1. Get a free API key from [Google AI Studio](https://aistudio.google.com/).
2. Set it as an environment variable on your machine.

**For Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```
**For Mac/Linux:**
```powershell
export GEMINI_API_KEY="your_api_key_here"
```

Once the key is set, cinexg-eda will automatically detect it and inject the AI insights into your HTML dashboard.
If no key is found, the package gracefully skips the AI step and generates the standard statistical report.

🔒 **Privacy First:** Your raw data is never sent to the LLM. `cinexg-eda` only transmits the statistical metadata (column names, missing value percentages, and math summaries) to generate the report.


This creates an interactive HTML dashboard containing:

* dataset statistics
* visualizations
* correlation analysis
* data quality insights

---

## Terminal Summary

If you only want a quick analysis printed to the terminal:

```python
import cinexg_eda

results = cinexg_eda.analyze("your_dataset.csv")
print(results)
```

The function works with:

* CSV files
* Excel files
* Pandas DataFrames

---

## Example Output

cinexg-eda automatically generates:

* dataset overview
* missing value report
* descriptive statistics
* correlation matrix
* distribution plots
* data quality warnings

All results are exported into a structured HTML dashboard.

---

## Supported Data Sources

* CSV files
* Excel files
* Pandas DataFrames

---

## Technical Requirements

* Python 3.9 or higher
* pandas
* numpy
* matplotlib
* seaborn
* scikit-learn

---

## Project Structure

```
cinexg-eda
│
├── cinexg_eda
│   ├── __init__.py
│   ├── analyzer.py
│   ├── visualization.py
│   ├── llm_explainer.py
│   ├── report.py
│   └── utils.py
│
├── examples
│   └── example_dataset.csv
│
├── tests
│
├── pyproject.toml
└── README.md
```

---

## Roadmap

Planned improvements include:

* automatic feature importance analysis
* dataset drift detection
* advanced outlier detection
* interactive web dashboards
* integration with Jupyter notebooks

---

## Contributing

Contributions are welcome.
If you would like to improve the package, feel free to open an issue or submit a pull request.

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
GitHub: https://github.com/cinexg
