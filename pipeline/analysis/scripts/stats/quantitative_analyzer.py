#!/usr/bin/env python3
"""
RQ1.1 Quantitative Analyzer

Reads a CSV dataset, computes class distributions for selected columns,
supports both single-label and multi-label cells, exports frequency tables to CSV,
and generates bar charts as PNG files.

Example:
    python quantitative_analyzer.py \
        --input ../../dataset/study_corpus.csv \
        --output-dir ../../output/ \
        --columns sa_doc domain \
        --multilabel-columns domain \
        --label-separators ';' '|' ','

Notes:
- Multi-label cells are split using the configured separators.
- Empty values can be ignored or counted as "<MISSING>".
- The script sanitizes file names and creates one CSV + one PNG per analyzed column.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable, List

import matplotlib.pyplot as plt
import pandas as pd


DEFAULT_MISSING_LABEL = "<MISSING>"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compute class distributions from CSV columns, including multi-label columns, "
            "and export frequency tables and bar charts."
        )
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input CSV file.",
    )
    parser.add_argument(
        "--output-dir",
        default="results",
        help="Directory where outputs will be stored. Default: rq11_results",
    )
    parser.add_argument(
        "--columns",
        nargs="+",
        default=None,
        help=(
            "Columns to analyze. If omitted, all columns in the CSV will be analyzed."
        ),
    )
    parser.add_argument(
        "--multilabel-columns",
        nargs="*",
        default=[],
        help="Columns whose cells may contain multiple labels.",
    )
    parser.add_argument(
        "--label-separators",
        nargs="*",
        default=[";", "|", ","],
        help="Separators used to split multi-label cells. Default: ';' '|' ','",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="CSV encoding. Default: utf-8",
    )
    parser.add_argument(
        "--csv-separator",
        default=",",
        help="CSV field separator. Default: ','",
    )
    parser.add_argument(
        "--keep-missing",
        action="store_true",
        help=(
            "Include missing/empty values in the counts using a placeholder label. "
            "By default, missing values are ignored."
        ),
    )
    parser.add_argument(
        "--missing-label",
        default=DEFAULT_MISSING_LABEL,
        help=f"Label used when --keep-missing is enabled. Default: {DEFAULT_MISSING_LABEL}",
    )
    parser.add_argument(
        "--sort-by",
        choices=["count", "label"],
        default="count",
        help="Sort output tables by count or label. Default: count",
    )
    parser.add_argument(
        "--ascending",
        action="store_true",
        help="Sort in ascending order. Default is descending.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=None,
        help="If set, charts will show only the top N labels for each column.",
    )
    parser.add_argument(
        "--min-count",
        type=int,
        default=1,
        help="Minimum count required for a class to appear in outputs. Default: 1",
    )
    parser.add_argument(
        "--title-prefix",
        default="",
        help="Optional prefix added to chart titles.",
    )
    return parser.parse_args()


def sanitize_filename(name: str) -> str:
    name = name.strip().replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name)


def ensure_directories(base_dir: Path) -> tuple[Path, Path]:
    tables_dir = base_dir / "tables"
    charts_dir = base_dir / "charts"
    tables_dir.mkdir(parents=True, exist_ok=True)
    charts_dir.mkdir(parents=True, exist_ok=True)
    return tables_dir, charts_dir


def build_split_pattern(separators: Iterable[str]) -> str:
    escaped = [re.escape(sep) for sep in separators if sep]
    if not escaped:
        # fallback that never splits
        return r"$^"
    return "|".join(escaped)


def is_missing(value: object) -> bool:
    if pd.isna(value):
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def normalize_label(label: str) -> str:
    # Compact repeated internal whitespace while preserving content.
    return re.sub(r"\s+", " ", label).strip()


def extract_labels(
    series: pd.Series,
    multilabel: bool,
    split_pattern: str,
    keep_missing: bool,
    missing_label: str,
) -> List[str]:
    labels: List[str] = []

    for value in series.tolist():
        if is_missing(value):
            if keep_missing:
                labels.append(missing_label)
            continue

        text = str(value).strip()
        if not multilabel:
            normalized = normalize_label(text)
            if normalized:
                labels.append(normalized)
            elif keep_missing:
                labels.append(missing_label)
            continue

        parts = re.split(split_pattern, text)
        cleaned_parts = [normalize_label(part) for part in parts if normalize_label(part)]

        if cleaned_parts:
            labels.extend(cleaned_parts)
        elif keep_missing:
            labels.append(missing_label)

    return labels


def build_frequency_table(labels: List[str], sort_by: str, ascending: bool, min_count: int) -> pd.DataFrame:
    if not labels:
        return pd.DataFrame(columns=["label", "count", "percentage"])

    counts = pd.Series(labels).value_counts(dropna=False)
    table = counts.rename_axis("label").reset_index(name="count")
    table = table[table["count"] >= min_count].copy()
    total = int(table["count"].sum())
    table["percentage"] = (table["count"] / total * 100).round(2) if total else 0.0

    if sort_by == "label":
        table = table.sort_values(by=["label", "count"], ascending=[ascending, not ascending], kind="stable")
    else:
        table = table.sort_values(by=["count", "label"], ascending=[ascending, True], kind="stable")

    table.reset_index(drop=True, inplace=True)
    return table


def save_table(table: pd.DataFrame, path: Path) -> None:
    table.to_csv(path, index=False, encoding="utf-8")

def plot_distribution(
    table: pd.DataFrame,
    column_name: str,
    output_path: Path,
    top_n: int | None,
    title_prefix: str,
) -> None:
    if table.empty:
        return

    plot_df = table.copy()
    if top_n is not None and top_n > 0:
        plot_df = plot_df.head(top_n)

    width = max(10, min(18, 0.55 * len(plot_df) + 6))
    height = 6.5

    plt.figure(figsize=(width, height))

    colors = ["#3b5b92", "#6c8ebf", "#888888", "#b0b0b0"]
    bars = plt.bar(
        plot_df["label"],
        plot_df["count"],
        color=colors,
        edgecolor="#444444",
        linewidth=0.8,
    )

    full_title = f"{title_prefix} {column_name}".strip()
    plt.title(f"Class distribution - {full_title}", fontsize=13, pad=12)
    plt.xlabel("Class")
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.3)

    for bar, value in zip(bars, plot_df["count"]):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            value,
            str(int(value)),
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def validate_columns(df: pd.DataFrame, columns: Iterable[str]) -> None:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(
            f"The following columns were not found in the CSV: {missing}. "
            f"Available columns: {list(df.columns)}"
        )


def main() -> int:
    args = parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)

    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        df = pd.read_csv(input_path, sep=args.csv_separator, encoding=args.encoding)
    except Exception as exc:  # pragma: no cover - defensive runtime handling
        print(f"Error while reading CSV: {exc}", file=sys.stderr)
        return 1

    columns = args.columns if args.columns else list(df.columns)
    multilabel_columns = set(args.multilabel_columns)

    try:
        validate_columns(df, columns)
        validate_columns(df, multilabel_columns)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    tables_dir, charts_dir = ensure_directories(output_dir)
    split_pattern = build_split_pattern(args.label_separators)

    summary_rows = []

    for column in columns:
        labels = extract_labels(
            series=df[column],
            multilabel=column in multilabel_columns,
            split_pattern=split_pattern,
            keep_missing=args.keep_missing,
            missing_label=args.missing_label,
        )

        table = build_frequency_table(
            labels=labels,
            sort_by=args.sort_by,
            ascending=args.ascending,
            min_count=args.min_count,
        )

        safe_name = sanitize_filename(column)
        table_path = tables_dir / f"{safe_name}_distribution.csv"
        chart_path = charts_dir / f"{safe_name}_distribution.png"

        save_table(table, table_path)
        plot_distribution(
            table=table,
            column_name=column,
            output_path=chart_path,
            top_n=args.top_n,
            title_prefix=args.title_prefix,
        )

        total_assignments = int(table["count"].sum()) if not table.empty else 0
        num_classes = int(table["label"].nunique()) if not table.empty else 0

        summary_rows.append(
            {
                "column": column,
                "multilabel": column in multilabel_columns,
                "num_classes": num_classes,
                "total_assignments": total_assignments,
                "table_csv": str(table_path),
                "chart_png": str(chart_path),
            }
        )

        print(
            f"Processed column '{column}': {num_classes} classes, "
            f"{total_assignments} assignments."
        )

    summary_df = pd.DataFrame(summary_rows)
    summary_path = output_dir / "tables" / "analysis_summary_quantitative.csv"
    summary_df.to_csv(summary_path, index=False, encoding="utf-8")

    print(f"\nDone. Summary saved to: {summary_path}")
    print(f"Tables directory: {tables_dir}")
    print(f"Charts directory: {charts_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
