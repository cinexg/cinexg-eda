# statlens — Agent Notes

Automated exploratory data analysis (EDA) library for Python (formerly published as
cinexg-eda; renamed to statlens). Point it at a CSV, Excel file, or `pandas.DataFrame`
and it produces a terminal summary, a self-contained HTML report, or both via a CLI
(stats, correlations, missingness, outliers, ID-column detection, ML task suggestions,
plots, and an optional Gemini-generated executive summary).

## Layout

```
statlens/
  __init__.py       # public API surface: analyze, report; __version__ from package metadata
  analyzer.py        # analyze(): loads data, computes stats/quality checks/ML guess
  utils.py            # threshold constants + small helpers analyzer.py builds on
  visualization.py    # generate_visualizations(): matplotlib/seaborn PNGs to disk
  llm_explainer.py    # generate_explanation(): optional Gemini executive summary
  report.py           # report(): orchestrates analyze + visuals + LLM into one HTML file
  cli.py              # `statlens <path> [options]` entry point (wired via pyproject.toml)
  templates/
    report_template.html  # string.Template HTML, loaded via importlib.resources
tests/
  test_analyzer.py       # analyze() behavior, including all Quality_Checks additions
  test_visualization.py  # generate_visualizations() output paths
  test_llm_explainer.py  # no-key / missing-package / privacy-invariant behavior
  test_cli.py             # end-to-end CLI smoke test (HTML + JSON output)
test.py                   # root-level manual smoke script, NOT part of the pytest suite
.github/workflows/python-package.yml  # CI: ruff + pytest on Python 3.9-3.12, ubuntu-latest
```

## Data flow

`report(file_path, output="report.html", results=None, include_ai=True)` in
[report.py](statlens/report.py) is the main entry point and calls, in order:

1. `analyzer._load_dataset` — accepts a DataFrame, or a `.csv`/`.xls`/`.xlsx` path.
2. `analyzer.analyze(data_input, corr_threshold=0.7, skew_threshold=1.0,
   id_uniqueness_threshold=0.95)` — skipped if a precomputed `results` dict is passed in
   (the CLI does this to avoid running the analysis twice). Returns one results dict with
   keys `Overview`, `Column_Types`, `Missing_Values`, `Statistical_Summary` (now includes
   `Boolean` and `Datetime` sections), `High_Correlations`, `Quality_Checks` (now includes
   `Outliers`, `Likely_ID_Columns`, `Possible_Numeric_As_Text` alongside the original
   duplicate/constant/skew checks), `ML_Suggestions` (now includes a `Reasoning` string).
   Also prints a terminal report as a side effect.
3. `llm_explainer.generate_explanation` — sends **only the stats dict** (never raw rows)
   to Gemini if `GEMINI_API_KEY` is set and `include_ai=True`; otherwise returns a
   placeholder string. Failures are caught and degrade to a warning string, never raise.
4. `visualization.generate_visualizations` — writes PNGs (missing-value heatmap,
   correlation heatmap, histograms) to `eda_assets/` (default) and returns their paths.
5. `report_template.html` is loaded via `importlib.resources` and filled in with
   `string.Template.substitute(...)` (not an inline f-string, and not Jinja2).

`analyze(data_input, ...)` alone (no report/visuals/LLM) is the lighter-weight entry
point for terminal-only usage. `cli.main()` (installed as the `statlens` command) wraps
both: it always calls `analyze()` once, optionally dumps the result to `--json`, then
calls `report(..., results=..., include_ai=not args.no_ai)`.

## Running things

**Local environment note specific to this machine**: Windows Smart App Control is
enforced here and blocks pandas' native `.pyd` files regardless of Python version or
venv — confirmed via `HKLM:\SYSTEM\CurrentControlSet\Control\CI\Policy` showing
`VerifiedAndReputablePolicyState = 1`. Smart App Control cannot be disabled without a
clean Windows reinstall, so don't attempt that. The working venv lives at `.venv/` but
was created **inside WSL** (Ubuntu distro, already installed on this machine) since
Smart App Control doesn't apply to Linux binaries. Run everything through it via:

```bash
wsl -d Ubuntu -- bash -c 'cd "/mnt/e/cinexg EDA" && ./.venv/bin/python -m pytest -q'
wsl -d Ubuntu -- bash -c 'cd "/mnt/e/cinexg EDA" && ./.venv/bin/ruff check .'
wsl -d Ubuntu -- bash -c 'cd "/mnt/e/cinexg EDA" && ./.venv/bin/statlens <path> [options]'
```

Do not recreate `.venv` with Windows Python — it will hit the same DLL block. The WSL
Ubuntu distro also has no system `pip`/`venv` (Debian strips `ensurepip`, and `apt`
needs an interactive sudo password this session couldn't provide); pip was bootstrapped
via `get-pip.py --user --break-system-packages` and `virtualenv` (not stdlib `venv`) was
used to create `.venv`. GitHub Actions CI runs on `ubuntu-latest` and is unaffected by
any of this.

```bash
pip install -e .          # editable install; pulls pandas/numpy/matplotlib/seaborn/
                            # scikit-learn/google-generativeai from pyproject.toml
pip install pytest ruff
pytest                     # runs the full tests/ suite (matches CI)
ruff check .               # lint (see [tool.ruff] in pyproject.toml for the pinned rule set)
python test.py             # manual smoke test: builds a dummy CSV, writes
                            # my_first_eda_report.html + test_dataset.csv to cwd
```

`ruff`'s newer default rule discovery pulled in import-sorting (I001) and style-opinion
rules (FA100, RUF010) beyond the classic `E4/E7/E9/F` set; `[tool.ruff.lint] select` in
`pyproject.toml` pins it back down intentionally. Don't widen that without checking in —
it was a deliberate scope decision, not an oversight.

## Known inconsistencies (don't "fix" without checking intent first)

- **Root `test.py` vs `tests/`**: only the `tests/` directory is picked up by pytest/CI.
  Root `test.py` is a manual, human-run script and writes artifacts
  (`test_dataset.csv`, `my_first_eda_report.html`) into the cwd — these are gitignored,
  but `report()`'s `eda_assets/` output directory and any CLI-generated report/JSON
  files are also cwd-relative, so check `git status` after manual runs.
- **`google-generativeai` (the dependency `llm_explainer.py` uses) is fully deprecated
  by Google** — confirmed via a `FutureWarning` surfaced during test runs: "All support
  for the `google.generativeai` package has ended... switch to the `google.genai`
  package." This wasn't in scope for the current improvement pass and hasn't been
  migrated; flagged to the user but not yet acted on. Whoever picks this up next should
  check whether `google-genai` has landed before adding new LLM-facing code here.

## Conventions worth preserving

- Privacy: the LLM path must only ever receive aggregated metadata (column names,
  percentages, summary stats), never raw dataframe rows. Keep this invariant if touching
  `llm_explainer.py` or `report.py` — `tests/test_llm_explainer.py` has a regression test
  for this specifically (it runs a real dataframe through `analyze()` and asserts a
  planted raw value never reaches the outgoing prompt).
- `llm_explainer.generate_explanation` must never raise — missing key, missing package,
  and API failures all degrade to a returned warning string so `report()` still completes
  without AI insights.
- Public API is intentionally small: `statlens.analyze` and `statlens.report`, both
  re-exported via `__init__.py`'s `__all__`. The CLI (`statlens.cli.main`) is a separate,
  additive entry point, not part of the importable API surface.
- New `Quality_Checks`/`Statistical_Summary` keys should stay JSON-serializable (or at
  least handled by `cli.py`'s `_json_default` numpy-scalar fallback) since the CLI's
  `--json` export round-trips the whole `analyze()` result.
