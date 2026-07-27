import json
import re

import pandas as pd

from statlens.cli import main


def test_cli_generates_html_and_json(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    df = pd.DataFrame({
        "age": [25, 30, 22, 40, 35],
        "salary": [50000, 60000, 45000, 80000, 70000],
        "department": ["IT", "HR", "Sales", "IT", "Marketing"],
    })
    csv_path = tmp_path / "data.csv"
    df.to_csv(csv_path, index=False)

    html_path = tmp_path / "out_report.html"
    json_path = tmp_path / "out_results.json"

    main([
        str(csv_path),
        "--output", str(html_path),
        "--json", str(json_path),
        "--no-ai",
    ])

    assert html_path.exists()
    assert json_path.exists()

    with open(json_path, encoding="utf-8") as f:
        results = json.load(f)
    assert results["Overview"]["Rows"] == 5
    assert results["Overview"]["Columns"] == 3

    html_content = html_path.read_text(encoding="utf-8")
    assert "AI executive summary skipped" in html_content
    assert "$" not in html_content  # no unresolved template placeholders

    # report() no longer shells out to matplotlib/seaborn for PNGs; the report
    # is a single file with an embedded JSON blob driving inline SVG/JS charts.
    assert not (tmp_path / "eda_assets").exists()

    match = re.search(
        r'<script type="application/json" id="statlens-data">(.*?)</script>',
        html_content,
        re.DOTALL,
    )
    assert match is not None
    chart_data = json.loads(match.group(1))
    for key in ("meta", "overview", "missing", "correlation", "numeric", "categorical", "quality"):
        assert key in chart_data
    assert chart_data["overview"]["rows"] == 5
    assert chart_data["correlation"]["columns"] == ["age", "salary"]
