#!/usr/bin/env python3
"""
Replication Package Script:
Inter-rater Reliability Analysis for Multilabel Quality Attributes

Purpose
-------
- Compute Cohen's Kappa for multilabel quality-attribute coding
- Support 3 raters (e.g., R1, R2, R3)
- Treat each fragment as a set of labels
- Expand multilabel annotations into binary presence/absence matrices
- Produce replication-package-ready CSV outputs

Method
------
For multilabel coding, direct string-to-string comparison is not appropriate.
Instead, this script:
1. Parses each coded cell into a set of labels
2. Builds binary vectors per attribute (present/absent per fragment)
3. Computes Cohen's Kappa per attribute for each rater pair
4. Aggregates macro-average kappas per pair
5. Computes additional agreement metrics:
   - observed agreement
   - exact set agreement
   - mean Jaccard similarity

Outputs
-------
output_dir/
  tables_csv/
    quality_kappa_by_attribute.csv
    quality_kappa_long_format.csv
    quality_kappa_pair_summary.csv
    quality_multilabel_binary_matrix.csv
  analysis_summary.csv

Usage:

  python quality_kappa.py \
  --input ../../dataset/irr_quality_requirements.csv \
  --output-dir ../../output/kappa/ \
  --rater-cols quality_r1 quality_r2 quality_r3 \
"""

from __future__ import annotations

import argparse
import itertools
import re
from pathlib import Path
from typing import Dict, List, Sequence, Set, Tuple

import pandas as pd
from sklearn.metrics import cohen_kappa_score


DEFAULT_SEPARATORS = [";", "|", ","]
DEFAULT_MISSING_TOKENS = {"", "none", "nan", "n/a", "na", "null", "-", "--"}

ATTRIBUTE_NORMALIZATION = {
    "compatibility": "Compatibility",
    "interoperabilidade (compatibility)": "Compatibility",
    "flexibility": "Flexibility",
    "escalabilidade (flexibility)": "Flexibility",
    "functional suitability": "Functional Suitability",
    "interaction capability": "Interaction Capability",
    "maintainability": "Maintainability",
    "performance efficiency": "Performance Efficiency",
    "reliability": "Reliability",
    "safety": "Safety",
    "security": "Security",
}

def normalize_attribute_label(label: str) -> str:
    key = str(label).strip().lower()
    return ATTRIBUTE_NORMALIZATION.get(key, str(label).strip())

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute multilabel Cohen's Kappa for quality-attribute coding."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input CSV file.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where replication package outputs will be saved.",
    )
    parser.add_argument(
        "--id-col",
        default=None,
        help="Optional fragment identifier column.",
    )
    parser.add_argument(
        "--rater-cols",
        nargs=3,
        required=True,
        metavar=("R1_COL", "R2_COL", "R3_COL"),
        help="Exactly three CSV columns containing multilabel annotations.",
    )
    parser.add_argument(
        "--rater-labels",
        nargs=3,
        default=["R1", "R2", "R3"],
        metavar=("R1_LABEL", "R2_LABEL", "R3_LABEL"),
        help="Display labels for the three raters.",
    )
    parser.add_argument(
        "--label-separators",
        nargs="+",
        default=DEFAULT_SEPARATORS,
        help="Separators used inside multilabel cells. Default: ; | ,",
    )
    parser.add_argument(
        "--normalize-case",
        action="store_true",
        help="Lowercase labels during normalization.",
    )
    parser.add_argument(
        "--strip-prefix-numbers",
        action="store_true",
        help="Remove numeric prefixes such as '1. Reliability' or '01 - Security'.",
    )
    parser.add_argument(
        "--keep-empty-as-label",
        action="store_true",
        help="Keep empty cells as an explicit label instead of treating them as missing.",
    )
    return parser.parse_args()


def ensure_dirs(output_dir: Path) -> Dict[str, Path]:
    tables_dir = output_dir
    tables_dir.mkdir(parents=True, exist_ok=True)
    return {
        "root": output_dir,
        "kappa": tables_dir,
    }


def validate_columns(df: pd.DataFrame, required_cols: Sequence[str]) -> None:
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required columns in input CSV: {missing}\n"
            f"Available columns: {list(df.columns)}"
        )


def clean_scalar_label(
    value: str,
    normalize_case: bool = False,
    strip_prefix_numbers: bool = False,
) -> str:
    text = str(value).strip()

    if strip_prefix_numbers:
        text = re.sub(r"^\s*\d+[\.\)\-:_ ]+\s*", "", text)

    text = re.sub(r"\s+", " ", text).strip()

    if normalize_case:
        text = text.lower()

    return text

def split_multilabel_cell(
    raw_value,
    separators: Sequence[str],
    normalize_case: bool = False,
    strip_prefix_numbers: bool = False,
    keep_empty_as_label: bool = False,
) -> Set[str]:
    if pd.isna(raw_value):
        return {"<EMPTY>"} if keep_empty_as_label else set()

    text = str(raw_value).strip()

    if not text:
        return {"<EMPTY>"} if keep_empty_as_label else set()

    if normalize_case:
        lowered = text.lower().strip()
        if lowered in DEFAULT_MISSING_TOKENS and not keep_empty_as_label:
            return set()

    pattern = "|".join(re.escape(sep) for sep in separators)
    parts = re.split(pattern, text)

    labels: Set[str] = set()
    for part in parts:
        label = clean_scalar_label(
            part,
            normalize_case=normalize_case,
            strip_prefix_numbers=strip_prefix_numbers,
        )
        if not label:
            continue
        if normalize_case and label in DEFAULT_MISSING_TOKENS and not keep_empty_as_label:
            continue

        label = normalize_attribute_label(label)
        labels.add(label)

    if not labels and keep_empty_as_label:
        return {"<EMPTY>"}

    return labels


def observed_agreement_binary(a: Sequence[int], b: Sequence[int]) -> float:
    if len(a) == 0:
        return float("nan")
    matches = sum(1 for x, y in zip(a, b) if x == y)
    return matches / len(a)


def jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    union = set_a | set_b
    if not union:
        return 1.0
    return len(set_a & set_b) / len(union)


def exact_set_agreement(set_a: Set[str], set_b: Set[str]) -> int:
    return int(set_a == set_b)


def build_binary_matrix(
    df: pd.DataFrame,
    id_col: str | None,
    rater_cols: Sequence[str],
    rater_labels: Sequence[str],
    separators: Sequence[str],
    normalize_case: bool,
    strip_prefix_numbers: bool,
    keep_empty_as_label: bool,
) -> Tuple[pd.DataFrame, Dict[str, List[Set[str]]], List[str]]:
    parsed_by_rater: Dict[str, List[Set[str]]] = {}

    for rater_col, rater_label in zip(rater_cols, rater_labels):
        parsed_by_rater[rater_label] = [
            split_multilabel_cell(
                raw_value=value,
                separators=separators,
                normalize_case=normalize_case,
                strip_prefix_numbers=strip_prefix_numbers,
                keep_empty_as_label=keep_empty_as_label,
            )
            for value in df[rater_col]
        ]

    all_attributes = sorted(
        {
            label
            for assignments in parsed_by_rater.values()
            for label_set in assignments
            for label in label_set
        }
    )

    rows = []
    for idx in range(len(df)):
        base_row = {
            "row_index": idx,
        }
        if id_col is not None:
            base_row["fID"] = df.iloc[idx][id_col]

        for rater_label in rater_labels:
            label_set = parsed_by_rater[rater_label][idx]
            base_row[f"{rater_label}_labels"] = "; ".join(sorted(label_set)) if label_set else ""

            for attribute in all_attributes:
                base_row[f"{rater_label}__{attribute}"] = int(attribute in label_set)

        rows.append(base_row)

    binary_df = pd.DataFrame(rows)
    return binary_df, parsed_by_rater, all_attributes


def compute_pairwise_attribute_kappa(
    parsed_by_rater: Dict[str, List[Set[str]]],
    all_attributes: Sequence[str],
    rater_labels: Sequence[str],
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    attribute_rows = []
    long_rows = []
    pair_summary_rows = []

    rater_pairs = list(itertools.combinations(rater_labels, 2))

    for left_rater, right_rater in rater_pairs:
        kappas = []
        agreements = []

        exact_matches = []
        jaccards = []

        left_sets = parsed_by_rater[left_rater]
        right_sets = parsed_by_rater[right_rater]

        for s1, s2 in zip(left_sets, right_sets):
            exact_matches.append(exact_set_agreement(s1, s2))
            jaccards.append(jaccard_similarity(s1, s2))

        for attribute in all_attributes:
            left_binary = [int(attribute in label_set) for label_set in left_sets]
            right_binary = [int(attribute in label_set) for label_set in right_sets]

            kappa_value = cohen_kappa_score(left_binary, right_binary)
            agreement_value = observed_agreement_binary(left_binary, right_binary)

            kappas.append(kappa_value)
            agreements.append(agreement_value)

            long_rows.append(
                {
                    "pair": f"{left_rater}_vs_{right_rater}",
                    "left_rater": left_rater,
                    "right_rater": right_rater,
                    "attribute": attribute,
                    "kappa": kappa_value,
                    "observed_agreement": agreement_value,
                    "support_left": sum(left_binary),
                    "support_right": sum(right_binary),
                    "support_union": sum(
                        int((a == 1) or (b == 1)) for a, b in zip(left_binary, right_binary)
                    ),
                }
            )

        macro_kappa = float(pd.Series(kappas).mean()) if kappas else float("nan")
        macro_agreement = float(pd.Series(agreements).mean()) if agreements else float("nan")
        exact_set_agreement_mean = float(pd.Series(exact_matches).mean()) if exact_matches else float("nan")
        mean_jaccard = float(pd.Series(jaccards).mean()) if jaccards else float("nan")

        pair_summary_rows.append(
            {
                "pair": f"{left_rater}_vs_{right_rater}",
                "left_rater": left_rater,
                "right_rater": right_rater,
                "n_fragments": len(left_sets),
                "n_attributes": len(all_attributes),
                "macro_kappa": macro_kappa,
                "macro_observed_agreement": macro_agreement,
                "exact_set_agreement": exact_set_agreement_mean,
                "mean_jaccard_similarity": mean_jaccard,
            }
        )

    long_df = pd.DataFrame(long_rows)

    if not long_df.empty:
        attribute_df = (
            long_df.pivot_table(
                index="attribute",
                columns="pair",
                values="kappa",
                aggfunc="first",
            )
            .reset_index()
            .rename_axis(None, axis=1)
        )
    else:
        attribute_df = pd.DataFrame(columns=["attribute"])

    pair_summary_df = pd.DataFrame(pair_summary_rows)

    if not pair_summary_df.empty:
        overall_macro = float(pair_summary_df["macro_kappa"].mean())
        overall_macro_obs = float(pair_summary_df["macro_observed_agreement"].mean())
        overall_exact = float(pair_summary_df["exact_set_agreement"].mean())
        overall_jaccard = float(pair_summary_df["mean_jaccard_similarity"].mean())

        summary_row = {
            "attribute": "OVERALL_MACRO_AVERAGE",
        }
        for pair_name in pair_summary_df["pair"]:
            pair_value = pair_summary_df.loc[pair_summary_df["pair"] == pair_name, "macro_kappa"].iloc[0]
            summary_row[pair_name] = pair_value

        attribute_df = pd.concat([attribute_df, pd.DataFrame([summary_row])], ignore_index=True)

        pair_summary_df = pd.concat(
            [
                pair_summary_df,
                pd.DataFrame(
                    [
                        {
                            "pair": "OVERALL_MACRO_AVERAGE",
                            "left_rater": "ALL",
                            "right_rater": "ALL",
                            "n_fragments": len(next(iter(parsed_by_rater.values()))) if parsed_by_rater else 0,
                            "n_attributes": len(all_attributes),
                            "macro_kappa": overall_macro,
                            "macro_observed_agreement": overall_macro_obs,
                            "exact_set_agreement": overall_exact,
                            "mean_jaccard_similarity": overall_jaccard,
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )

    return attribute_df, long_df, pair_summary_df

def save_csv(df, path, index=True):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index)

# def save_csv(df: pd.DataFrame, path: Path) -> None:
#     df.to_csv(path, index=False, quoting=csv.QUOTE_MINIMAL)


def build_analysis_summary(
    input_path: Path,
    output_dir: Path,
    df: pd.DataFrame,
    rater_cols: Sequence[str],
    rater_labels: Sequence[str],
    all_attributes: Sequence[str],
    pair_summary_df: pd.DataFrame,
) -> pd.DataFrame:
    overall_row = pair_summary_df.loc[pair_summary_df["pair"] == "OVERALL_MACRO_AVERAGE"]

    overall_macro = float("nan")
    overall_obs = float("nan")
    overall_exact = float("nan")
    overall_jaccard = float("nan")

    if not overall_row.empty:
        overall_macro = overall_row["macro_kappa"].iloc[0]
        overall_obs = overall_row["macro_observed_agreement"].iloc[0]
        overall_exact = overall_row["exact_set_agreement"].iloc[0]
        overall_jaccard = overall_row["mean_jaccard_similarity"].iloc[0]

    summary = pd.DataFrame(
        [
            {
                "input_file": str(input_path),
                "output_dir": str(output_dir),
                "n_fragments": len(df),
                "n_attributes_detected": len(all_attributes),
                "rater_1_col": rater_cols[0],
                "rater_2_col": rater_cols[1],
                "rater_3_col": rater_cols[2],
                "rater_1_label": rater_labels[0],
                "rater_2_label": rater_labels[1],
                "rater_3_label": rater_labels[2],
                "overall_macro_kappa": overall_macro,
                "overall_macro_observed_agreement": overall_obs,
                "overall_exact_set_agreement": overall_exact,
                "overall_mean_jaccard_similarity": overall_jaccard,
            }
        ]
    )
    return summary


def main() -> None:
    args = parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)

    if not input_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    dirs = ensure_dirs(output_dir)

    df = pd.read_csv(input_path)

    required_cols = list(args.rater_cols)
    if args.id_col:
        required_cols.append(args.id_col)

    validate_columns(df, required_cols)

    binary_df, parsed_by_rater, all_attributes = build_binary_matrix(
        df=df,
        id_col=args.id_col,
        rater_cols=args.rater_cols,
        rater_labels=args.rater_labels,
        separators=args.label_separators,
        normalize_case=args.normalize_case,
        strip_prefix_numbers=args.strip_prefix_numbers,
        keep_empty_as_label=args.keep_empty_as_label,
    )

    attribute_df, long_df, pair_summary_df = compute_pairwise_attribute_kappa(
        parsed_by_rater=parsed_by_rater,
        all_attributes=all_attributes,
        rater_labels=args.rater_labels,
    )

    analysis_summary_df = build_analysis_summary(
        input_path=input_path,
        output_dir=output_dir,
        df=df,
        rater_cols=args.rater_cols,
        rater_labels=args.rater_labels,
        all_attributes=all_attributes,
        pair_summary_df=pair_summary_df,
    )

    save_csv(binary_df, dirs["kappa"] / "quality_multilabel_binary_matrix.csv", index=False)
    save_csv(attribute_df, dirs["kappa"] / "quality_kappa_by_attribute.csv", index=False)
    save_csv(long_df, dirs["kappa"] / "quality_kappa_long_format.csv", index=False)
    save_csv(pair_summary_df, dirs["kappa"] / "quality_kappa_pair_summary.csv", index=False)
    save_csv(
        analysis_summary_df.T,
        dirs["kappa"] / "analysis_summary_quality_kappa.csv",
        index=True
    )

    print("\n=== Multilabel Quality Kappa Analysis Completed ===")
    print(f"Input file: {input_path}")
    print(f"Output directory: {output_dir}")
    print(f"Fragments analyzed: {len(df)}")
    print(f"Detected quality attributes: {len(all_attributes)}")
    if not pair_summary_df.empty:
        print("\nPairwise summary:")
        print(pair_summary_df.to_string(index=False))


if __name__ == "__main__":
    main()