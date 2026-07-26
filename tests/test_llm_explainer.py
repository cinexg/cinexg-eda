import sys
import types

import google
import pandas as pd

from statlens.analyzer import analyze
from statlens.llm_explainer import generate_explanation


def test_generate_explanation_no_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    result = generate_explanation(
        {"Overview": {}, "Quality_Checks": {}, "High_Correlations": [], "ML_Suggestions": {}},
        api_key=None,
    )

    assert "GEMINI_API_KEY" in result
    assert "skipped" in result.lower()


def test_generate_explanation_missing_package(monkeypatch):
    # Setting a module to None in sys.modules makes a subsequent import of it raise ImportError.
    monkeypatch.setitem(sys.modules, "google.generativeai", None)
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")

    result = generate_explanation(
        {"Overview": {}, "Quality_Checks": {}, "High_Correlations": [], "ML_Suggestions": {}}
    )

    assert "google-generativeai" in result


def test_generate_explanation_never_sends_raw_dataframe_values(monkeypatch):
    captured_prompts = []

    class FakeResponse:
        text = "fake summary"

    class FakeModel:
        def __init__(self, name):
            self.name = name

        def generate_content(self, prompt):
            captured_prompts.append(prompt)
            return FakeResponse()

    fake_genai = types.SimpleNamespace(
        configure=lambda api_key: None,
        GenerativeModel=lambda name: FakeModel(name),
    )
    # `import google.generativeai as genai` resolves via attribute access on the
    # already-imported `google` package object, not a fresh sys.modules lookup once
    # the real submodule has been imported once in this process - so both need patching.
    monkeypatch.setitem(sys.modules, "google.generativeai", fake_genai)
    monkeypatch.setattr(google, "generativeai", fake_genai, raising=False)

    # A distinctive raw cell value that should never leave analyze()'s aggregation step.
    raw_secret_value = "RAW_SECRET_ROW_VALUE_42"
    df = pd.DataFrame({
        "customer_note": ["ok", "ok", raw_secret_value, "ok", "ok"],
        "amount": [10, 20, 30, 40, 50],
    })
    results = analyze(df)

    prompt_result = generate_explanation(results, api_key="fake-key")

    assert prompt_result == "fake summary"
    assert len(captured_prompts) == 1
    assert raw_secret_value not in captured_prompts[0]
    # Aggregated stats (not raw rows) should still make it through.
    assert "Rows" in captured_prompts[0]
