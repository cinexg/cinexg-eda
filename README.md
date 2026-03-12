# cinexg-eda

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

cinexg_eda.report("your_dataset.csv", output="eda_report.html")
```

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
