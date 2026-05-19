#!/usr/bin/env python3
"""Summarize validated RQ2 evidence at project level.

Preferred use: after manual validation.
A project is counted in a category if at least one row for that category is labeled TP.
Rows marked FP are discarded. Rows marked UNCLEAR are reported separately.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import pandas as pd

CATEGORIES = [
    "arch_overview", "context", "views", "adrs", "deployment",
    "interface", "evaluation", "quality", "stakeholders"
]


def normalize_label(value: object) -> str:
    return str(value).strip().upper()


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize validated architectural documentation evidence.")
    parser.add_argument("--input", required=True, help="Manual checklist CSV.")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)
    required = {"repo", "category", "evidence_path", "manual_label"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df["manual_label"] = df["manual_label"].map(normalize_label)
    valid = df[df["manual_label"] == "TP"].copy()
    unclear = df[df["manual_label"] == "UNCLEAR"].copy()
    false_pos = df[df["manual_label"] == "FP"].copy()

    if valid.empty:
        project_presence = pd.DataFrame(columns=["repo", *CATEGORIES])
        category_distribution = pd.DataFrame(columns=["category", "projects", "percentage"])
        denominator = 0
    else:
        project_presence = (
            valid.assign(value=1)
            .pivot_table(index="repo", columns="category", values="value", aggfunc="max", fill_value=0)
            .reset_index()
        )
        for category in CATEGORIES:
            if category not in project_presence.columns:
                project_presence[category] = 0
        project_presence = project_presence[["repo", *CATEGORIES]]
        denominator = len(project_presence)

        category_distribution = pd.DataFrame(
            {
                "category": CATEGORIES,
                "projects": [int(project_presence[category].sum()) for category in CATEGORIES],
            }
        )
        category_distribution["percentage"] = category_distribution["projects"].apply(
            lambda n: round((n / denominator) * 100, 2) if denominator else 0.0
        )

    project_presence.to_csv(output_dir / "tables" / "project_presence.csv", index=False)
    category_distribution.to_csv(output_dir / "tables" / "category_distribution.csv", index=False)

    validation_report = {
        "total_rows": int(len(df)),
        "tp_rows": int(len(valid)),
        "fp_rows": int(len(false_pos)),
        "unclear_rows": int(len(unclear)),
        "validated_projects_denominator": int(denominator),
        "counting_rule": "A project is counted in category X if at least one evidence row is manually labeled TP for category X.",
    }
    (output_dir / "json" /"validation_report.json").write_text(
        json.dumps(validation_report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"[OK] Outputs written to: {output_dir}")
    print(json.dumps(validation_report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
