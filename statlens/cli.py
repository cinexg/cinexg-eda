"""Command-line entry point: `statlens <path> [options]`."""

import argparse
import json
from typing import Optional, Sequence

from .analyzer import analyze
from .report import report


def _json_default(value: object) -> object:
    """Fallback encoder for numpy scalar types that json.dumps can't handle natively."""
    if hasattr(value, "item"):
        return value.item()
    return str(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="statlens",
        description="Generate an automated exploratory data analysis report for a dataset.",
    )
    parser.add_argument("path", help="Path to a CSV or Excel file.")
    parser.add_argument(
        "--output", default="report.html",
        help="Path to write the HTML report to (default: report.html)."
    )
    parser.add_argument(
        "--json", dest="json_path", default=None,
        help="Also write the raw analysis results as JSON to this path."
    )
    parser.add_argument(
        "--no-ai", action="store_true",
        help="Skip the optional Gemini AI executive summary, even if GEMINI_API_KEY is set."
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = build_parser().parse_args(argv)

    results = analyze(args.path)

    if args.json_path:
        with open(args.json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=_json_default)
        print(f"📄 Results written to '{args.json_path}'")

    report(args.path, output=args.output, results=results, include_ai=not args.no_ai)


if __name__ == "__main__":
    main()
