from importlib import resources
from string import Template
from typing import Optional, Union

import pandas as pd

from .analyzer import analyze, _load_dataset
from .visualization import generate_visualizations
from .llm_explainer import generate_explanation


def _render_report(results: dict, ai_insights: str, image_paths: dict) -> str:
    template_text = resources.files("statlens").joinpath(
        "templates", "report_template.html"
    ).read_text(encoding="utf-8")

    histogram_section = ""
    if image_paths.get("hist_plot"):
        histogram_section = f'<img src="{image_paths["hist_plot"]}" alt="Histograms">'

    correlation_section = ""
    if image_paths.get("corr_plot"):
        correlation_section = (
            '<h3>Correlation Heatmap</h3>\n'
            f'<img src="{image_paths["corr_plot"]}" alt="Correlation Heatmap">'
        )

    quality_checks = results['Quality_Checks']
    ml_suggestions = results['ML_Suggestions']

    return Template(template_text).substitute(
        ai_insights=ai_insights,
        rows=f"{results['Overview']['Rows']:,}",
        columns=results['Overview']['Columns'],
        numerical_columns=results['Column_Types']['Numerical'],
        categorical_columns=results['Column_Types']['Categorical'],
        target_column=ml_suggestions['Target_Column_Guess'],
        ml_task=ml_suggestions['Task'],
        suggested_models=', '.join(ml_suggestions['Suggested_Models']),
        duplicate_rows=quality_checks['Duplicate_Rows'],
        constant_columns=(
            ', '.join(quality_checks['Constant_Columns'])
            if quality_checks['Constant_Columns'] else 'None detected'
        ),
        missing_plot=image_paths['missing_plot'],
        histogram_section=histogram_section,
        correlation_section=correlation_section,
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

    image_paths = generate_visualizations(df, output_dir="eda_assets")

    html_content = _render_report(results, ai_insights, image_paths)

    with open(output, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n✅ SUCCESS: Report generated and saved to '{output}'")
