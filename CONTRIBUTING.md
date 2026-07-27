# Contributing to statlens

Thanks for your interest in improving statlens. This document covers how to set up a
development environment, the coding conventions the project follows, and how to submit
changes.

## Getting started

1. Fork the repository and clone your fork.
2. Create a virtual environment and activate it.

```bash
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
```

3. Install the package in editable mode along with the development tools.

```bash
pip install -e .
pip install pytest ruff
```

## Running the test suite

The test suite lives in `tests/` and mirrors the package structure (one test file per
module). Run it with:

```bash
pytest
```

All new features and bug fixes should include test coverage. Tests should be
deterministic and not depend on network access or an API key; anything that touches
`llm_explainer.py` should mock or skip the actual Gemini call.

## Linting

The project uses ruff with an intentionally narrow rule set (see `[tool.ruff.lint]` in
`pyproject.toml`, restricted to `E4`, `E7`, `E9`, and `F`). Run it with:

```bash
ruff check .
```

Please do not widen the selected rule set as part of an unrelated change. If you think
it should change, open an issue to discuss it first.

## Coding guidelines

* Keep the public API small. `statlens.analyze` and `statlens.report` are the supported
  entry points; new functionality should extend these rather than introduce a second way
  to do the same thing.
* Do not send raw dataset rows to any external service. `llm_explainer.py` sends only
  aggregated statistics to the Gemini API, and `tests/test_llm_explainer.py` has a
  regression test for this. Any change touching the AI summary path must preserve this
  guarantee.
* `llm_explainer.generate_explanation` must never raise. Missing key, missing package,
  and API failures should degrade to a warning string so `report()` still completes.
* Prefer small, focused functions over large ones, and reuse existing helpers in
  `utils.py` instead of duplicating threshold constants or column-splitting logic.
* New keys added to the `analyze()` results dictionary should stay JSON serializable, or
  be handled by the existing numpy scalar fallback in `utils.json_default`, since the
  CLI's `--json` export and the HTML report's embedded chart data both serialize this
  dictionary.

## Submitting changes

1. Create a branch for your change.
2. Make your change, with tests and documentation updates as needed.
3. Run `pytest` and `ruff check .` locally and confirm both pass.
4. Open a pull request describing what changed and why. Reference any related issue.
5. Be responsive to review feedback. Small, focused pull requests are easier to review
   and merge than large ones.

## Reporting bugs and requesting features

Please use the issue templates under `.github/ISSUE_TEMPLATE` when opening an issue.
Include the statlens version, Python version, and a minimal reproducible example where
possible.

## Code of conduct

Participation in this project is governed by CODE_OF_CONDUCT.md. By participating, you
agree to follow it.
