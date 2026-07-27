import html
import json
import os
from importlib import resources
from string import Template
from typing import Optional, Union

import pandas as pd

from .analyzer import analyze, _load_dataset
from .llm_explainer import generate_explanation
from .report_data import build_chart_data
from .utils import json_default


def _render_report(ai_insights: str, chart_data: dict) -> str:
    template_text = resources.files("statlens").joinpath(
        "templates", "report_template.html"
    ).read_text(encoding="utf-8")

    # Escaped so a literal `</script>` inside user data (e.g. a column name)
    # can't break out of the embedded JSON <script> block.
    chart_data_json = json.dumps(chart_data, default=json_default).replace("</", "<\\/")

    return Template(template_text).substitute(
        ai_insights=html.escape(ai_insights),
        chart_data_json=chart_data_json,
    )


def report(
    file_path: Union[str, pd.DataFrame],
    output: str = "report.html",
    results: Optional[dict] = None,
    include_ai: bool = True,
) -> None:
    """
    Generate a complete EDA report in HTML format.

    `results` can be passed in to reuse an already-computed analyze() dict
    (e.g. from the CLI, which also needs it for --json export) instead of
    running the analysis twice.
    """
    print(f"🚀 Starting full EDA report generation for '{file_path}'...")

    if results is None:
        results = analyze(file_path)

    if include_ai:
        print("🧠 Generating AI executive summary (this takes a few seconds)...")
        ai_insights = generate_explanation(results)
    else:
        ai_insights = "AI executive summary skipped (--no-ai)."

    df = _load_dataset(file_path)

    source_label = os.path.basename(file_path) if isinstance(file_path, str) else "DataFrame"
    chart_data = build_chart_data(df, results, source_label)

    html_content = _render_report(ai_insights, chart_data)

    with open(output, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n✅ SUCCESS: Report generated and saved to '{output}'")
