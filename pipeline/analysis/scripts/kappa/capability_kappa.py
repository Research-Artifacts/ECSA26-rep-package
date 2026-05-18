#!/usr/bin/env python3
"""
Replication Package - Inter-rater Reliability Analysis for ISO/IEC 30141 Capability Mappings

Purpose
-------
Compute Cohen's Kappa for ISO/IEC 30141 capability mappings across three raters,
export replication-package-ready tables, and report per-capability as well as
macro-average agreement.

Main features
-------------
- Command-line interface with configurable input/output paths
- Validation of required columns
- Pairwise Cohen's Kappa for all configured capability groups
- Macro-average Kappa across capability groups
- Long-format table for easier reuse in papers and appendices
- Summary table for quick reporting
- Reproducible CSV outputs organized in a dedicated folder

Usage:

python capability_kappa.py \
  --input ../../dataset/irr_capabilities.csv \
  --output-dir ../../output/kappa/

"""

from __future__ import annotations

import argparse
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import pandas as pd
from sklearn.metrics import cohen_kappa_score


DEFAULT_CAPABILITY_GROUPS = [
    ("capability_1", "iso_map_C1-[R1]", "iso_map_C1-[R2]", "iso_map_C1-[R3]"),
    ("capability_2", "iso_map_C2-[R1]", "iso_map_C2-[R2]", "iso_map_C2-[R3]"),
    ("capability_3", "iso_map_C3-[R1]", "iso_map_C3-[R2]", "iso_map_C3-[R3]"),
]

DEFAULT_RATER_NAMES = ["R1", "R2", "R3"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute Cohen's Kappa for ISO/IEC 30141 capability mappings."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input CSV file."
    )
    parser.add_argument(
        "--output-dir",
        default="rq11_kappa_results",
        help="Directory where replication package outputs will be saved."
    )
    parser.add_argument(
        "--na-placeholder",
        default="NONE",
        help="Placeholder used to replace missing values before computing Kappa."
    )
    parser.add_argument(
        "--capability-groups",
        nargs="+",
        default=None,
        help=(
            "Optional custom capability groups. "
            "Format each item as: capability_label|rater1_col|rater2_col|rater3_col"
        ),
    )
    parser.add_argument(
        "--rater-labels",
        nargs=3,
        default=DEFAULT_RATER_NAMES,
        help="Labels for the three raters, in order. Default: R1 R2 R3"
    )
    return parser.parse_args()


def parse_capability_groups(raw_groups: Sequence[str] | None) -> List[Tuple[str, str, str, str]]:
    if not raw_groups:
        return DEFAULT_CAPABILITY_GROUPS

    parsed: List[Tuple[str, str, str, str]] = []
    for item in raw_groups:
        parts = [part.strip() for part in item.split("|")]
        if len(parts) != 4:
            raise ValueError(
                "Each --capability-groups entry must have exactly 4 parts: "
                "capability_label|rater1_col|rater2_col|rater3_col"
            )
        parsed.append((parts[0], parts[1], parts[2], parts[3]))
    return parsed


def ensure_required_columns(df: pd.DataFrame, capability_groups: Sequence[Tuple[str, str, str, str]]) -> None:
    required = set()
    for _, c1, c2, c3 in capability_groups:
        required.update([c1, c2, c3])

    missing = [col for col in sorted(required) if col not in df.columns]
    if missing:
        raise ValueError(
            "Missing required columns in input CSV: " + ", ".join(missing)
        )


def clean_series(series: pd.Series, placeholder: str) -> pd.Series:
    return series.fillna(placeholder).astype(str).str.strip().replace("", placeholder)


def compute_pairwise_kappa(
    df: pd.DataFrame,
    col_a: str,
    col_b: str,
    placeholder: str,
) -> float:
    a = clean_series(df[col_a], placeholder)
    b = clean_series(df[col_b], placeholder)
    return float(cohen_kappa_score(a, b))


def build_pair_labels(rater_labels: Sequence[str]) -> List[Tuple[str, int, int]]:
    pairs = []
    for i, j in combinations(range(len(rater_labels)), 2):
        pairs.append((f"{rater_labels[i]}_vs_{rater_labels[j]}", i, j))
    return pairs


def compute_kappa_tables(
    df: pd.DataFrame,
    capability_groups: Sequence[Tuple[str, str, str, str]],
    rater_labels: Sequence[str],
    placeholder: str,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    pair_specs = build_pair_labels(rater_labels)

    wide_rows: List[Dict[str, object]] = []
    long_rows: List[Dict[str, object]] = []

    for capability_label, col1, col2, col3 in capability_groups:
        cols = [col1, col2, col3]
        row: Dict[str, object] = {
            "capability": capability_label,
            "n_records": len(df),
        }

        for pair_name, idx_a, idx_b in pair_specs:
            value = compute_pairwise_kappa(df, cols[idx_a], cols[idx_b], placeholder)
            row[pair_name] = value
            long_rows.append({
                "capability": capability_label,
                "rater_pair": pair_name,
                "kappa": value,
                "n_records": len(df),
                "column_a": cols[idx_a],
                "column_b": cols[idx_b],
            })

        wide_rows.append(row)

    wide_df = pd.DataFrame(wide_rows)
    long_df = pd.DataFrame(long_rows)

    macro_row: Dict[str, object] = {
        "capability": "macro_average",
        "n_records": len(df),
    }
    for pair_name, _, _ in pair_specs:
        macro_row[pair_name] = float(wide_df[pair_name].mean())

    summary_rows = [macro_row]

    overall_macro = {
        "metric": "overall_macro_kappa",
        "value": float(long_df["kappa"].mean()) if not long_df.empty else float("nan"),
    }
    mean_by_pair = (
        long_df.groupby("rater_pair", as_index=False)["kappa"]
        .mean()
        .rename(columns={"kappa": "value"})
    )
    mean_by_pair.insert(0, "metric", mean_by_pair.pop("rater_pair"))

    summary_df = pd.concat(
        [
            pd.DataFrame(summary_rows),
            pd.DataFrame([overall_macro]),
            mean_by_pair,
        ],
        ignore_index=True,
        sort=False,
    )

    return wide_df, long_df, summary_df


def save_tables(
    wide_df: pd.DataFrame,
    long_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    output_dir: Path,
) -> None:
    tables_dir = output_dir
    tables_dir.mkdir(parents=True, exist_ok=True)

    wide_df.to_csv(tables_dir / "kappa_by_capability.csv", index=False)
    long_df.to_csv(tables_dir / "capability_kappa_long_format.csv", index=False)
    summary_df.to_csv(tables_dir / "capability_kappa_summary.csv", index=False)


def build_analysis_summary(
    input_path: str,
    output_dir: Path,
    capability_groups: Sequence[Tuple[str, str, str, str]],
    rater_labels: Sequence[str],
    summary_df: pd.DataFrame,
) -> pd.DataFrame:
    overall_macro_value = summary_df.loc[
        summary_df["metric"].eq("overall_macro_kappa"), "value"
    ]
    overall_macro = float(overall_macro_value.iloc[0]) if not overall_macro_value.empty else float("nan")

    rows = [
        {"item": "input_file", "value": input_path},
        {"item": "output_directory", "value": str(output_dir)},
        {"item": "n_capability_groups", "value": len(capability_groups)},
        {"item": "rater_labels", "value": ", ".join(rater_labels)},
        {"item": "overall_macro_kappa", "value": overall_macro},
    ]
    return pd.DataFrame(rows)


def main() -> None:
    args = parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    capability_groups = parse_capability_groups(args.capability_groups)

    df = pd.read_csv(input_path)
    ensure_required_columns(df, capability_groups)

    wide_df, long_df, summary_df = compute_kappa_tables(
        df=df,
        capability_groups=capability_groups,
        rater_labels=args.rater_labels,
        placeholder=args.na_placeholder,
    )

    save_tables(wide_df, long_df, summary_df, output_dir)

    analysis_summary_df = build_analysis_summary(
        input_path=str(input_path),
        output_dir=output_dir,
        capability_groups=capability_groups,
        rater_labels=args.rater_labels,
        summary_df=summary_df,
    )
    analysis_summary_df.to_csv(output_dir / "analysis_summary_capability_kappa.csv", index=False)

    print("\n=== Inter-rater Reliability Analysis Completed ===")
    print(f"Input file: {input_path}")
    print(f"Output directory: {output_dir}")
    print("\nSaved files:")
    print(f"- {output_dir / 'kappa_by_capability.csv'}")
    print(f"- {output_dir / 'capability_kappa_long_format.csv'}")
    print(f"- {output_dir / 'capability_kappa_summary.csv'}")
    print(f"- {output_dir / 'analysis_summary_capability_kappa.csv'}")

    overall_macro_value = summary_df.loc[
        summary_df["metric"].eq("overall_macro_kappa"), "value"
    ]
    if not overall_macro_value.empty:
        print(f"\nOverall macro-average Kappa: {overall_macro_value.iloc[0]:.4f}")


if __name__ == "__main__":
    main()
