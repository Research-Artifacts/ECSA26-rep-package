#!/usr/bin/env python3
"""
This module implements tools to process and prioritize files for manual validation based on heuristic scoring
derived from specified patterns in a raw JSON input. It facilitates categorization and prioritization to aid in
manual reviews.

Functions
---------

- parse_args(): Parses command-line arguments for input JSON, output directory, and configuration options.
- score_file(category, path): Computes a heuristic score for a file based on its path and category-specific patterns.
- confidence_label(score): Converts a heuristic score into a confidence label (e.g., high, medium, low).
- load_json(path): Loads JSON data from the specified file path.
- main(): Orchestrates the overall process, loading the JSON input, scoring evidence, and generating output files.

Constants
---------

- CATEGORIES: A list of predefined evidence categories for file classification.
- POSITIVE_PATTERNS: A dictionary of regex patterns that define positive matches for each evidence category.
- NEGATIVE_PATTERNS: A list of regex patterns that define patterns to assign penalty scores in file scoring.
- CATEGORY_PRIORITY: A dictionary assigning fixed priority values to each evidence category for sorting purposes.

"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd

CATEGORIES = [
    "arch_overview",
    "context",
    "views",
    "adrs",
    "deployment",
    "interface",
    "evaluation",
    "quality",
    "stakeholders",
]

POSITIVE_PATTERNS = {
    "arch_overview": [
        r"(^|/)README\.md$",
        r"(^|/)readme\.md$",
        r"(^|/)(docs|doc)/.*(overview|architecture|arch|concept|index).*\.md$",
        r"(^|/).*architecture.*\.(md|rst|txt)$",
        r"(^|/).*overview.*\.(md|rst|txt)$",
    ],
    "context": [
        r"(^|/)README\.md$",
        r"(^|/)(docs|doc)/.*(overview|getting-started|quickstart|concept|index).*\.md$",
        r"(^|/).*context.*\.(md|rst|txt)$",
        r"(^|/).*tutorial.*\.(md|rst)$",
    ],
    "views": [
        r"(^|/).*(arch|architecture|diagram|overview|topology|pipeline|model).*\.(png|jpg|jpeg|svg|drawio|puml|mmd|md)$",
        r"(^|/)(docs|doc)/images/.*\.(png|jpg|jpeg|svg)$",
        r"(^|/).*\.(drawio|puml|mmd)$",
    ],
    "adrs": [
        r"(^|/)(adr|adrs)(/|$)",
        r"(^|/)docs/.*/adr.*\.md$",
        r"(^|/).*decision.*record.*\.md$",
    ],
    "deployment": [
        r"(^|/)Dockerfile$",
        r"(^|/).*docker-compose.*\.(yml|yaml)$",
        r"(^|/).*(helm|k8s|kubernetes|deploy|deployment|manifests?|charts?)(/|$|.*\.(yml|yaml|md))",
        r"(^|/).*install.*\.(md|sh)$",
    ],
    "interface": [
        r"(^|/).*\.(proto|api)$",
        r"(^|/).*(openapi|swagger).*\.(yml|yaml|json)$",
        r"(^|/).*(grpc|api|protocol|interface).*\.(md|go|py|yaml|yml|json)$",
        r"(^|/)docs/api/README\.md$",
    ],
    "evaluation": [
        r"(^|/)(tests?|testdata|benchmarks?|benchmark|evaluation|profiling|performance)(/|$|.*)",
        r"(^|/).*benchmark.*\.(md|py|sh|proto|json)$",
        r"(^|/).*profil.*\.(md|py)$",
    ],
    "quality": [
        r"(^|/)SECURITY\.md$",
        r"(^|/).*(performance|best_practices|measurement|monitoring|reliability|security|privacy|trust).*\.(md|rst|txt|yaml|yml)$",
        r"(^|/).*troubleshoot.*\.(md|rst)$",
    ],
    "stakeholders": [
        r"(^|/).*(users?|operators?|admins?|developers?|roles?|access|portal).*\.(md|rst|txt)$",
        r"(^|/).*(overview|quickstart|getting-started|tutorial).*\.(md|rst)$",
    ],
}

NEGATIVE_PATTERNS = [
    r"(^|/)\.github/workflows/",
    r"(^|/)CODE_OF_CONDUCT\.md$",
    r"(^|/)CONTRIBUTING\.md$",
    r"(^|/)LICENSE",
    r"(^|/)Licence",
    r"(^|/)CHANGELOG",
    r"(^|/)Changelog",
    r"(^|/).*\.ini$",
    r"(^|/).*CMakeLists\.txt$",
    r"(^|/).*part-list.*",
]

CATEGORY_PRIORITY = {
    "arch_overview": 1,
    "context": 2,
    "views": 3,
    "adrs": 4,
    "quality": 5,
    "stakeholders": 6,
    "deployment": 7,
    "interface": 8,
    "evaluation": 9,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a priority queue for manual validation from raw RQ3 scanner JSON."
    )
    parser.add_argument("--input", required=True, help="Path to raw scanner JSON.")
    parser.add_argument("--output-dir", required=True, help="Directory for generated CSV/JSON files.")
    parser.add_argument("--max-files-per-repo", type=int, default=8)
    return parser.parse_args()


def score_file(category: str, path: str) -> int:
    score = 0
    for pattern in POSITIVE_PATTERNS.get(category, []):
        if re.search(pattern, path, flags=re.IGNORECASE):
            score += 3
    if re.search(r"(^|/)(docs|doc)/", path, flags=re.IGNORECASE):
        score += 1
    if re.search(r"(^|/)README\.md$", path, flags=re.IGNORECASE):
        score += 1
    for pattern in NEGATIVE_PATTERNS:
        if re.search(pattern, path, flags=re.IGNORECASE):
            score -= 2
    if re.search(r"\.(png|jpg|jpeg)$", path, flags=re.IGNORECASE) and category != "views":
        score -= 2
    return score


def confidence_label(score: int) -> str:
    if score >= 6:
        return "high"
    if score >= 3:
        return "medium"
    if score >= 0:
        return "low"
    return "very_low"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    data = load_json(input_path)
    rows = []

    for item in data:
        repo = item["repo"]
        evidence = item.get("evidence", {})
        for category in CATEGORIES:
            files = evidence.get(category, [])
            for file_path in files:
                score = score_file(category, file_path)
                rows.append(
                    {
                        "repo": repo,
                        "category": category,
                        "file": file_path,
                        "score": score,
                        "confidence": confidence_label(score),
                        "category_priority": CATEGORY_PRIORITY[category],
                    }
                )

    if not rows:
        raise SystemExit("No candidate evidence was found in the input JSON.")

    df = pd.DataFrame(rows)

    best_per_category = (
        df.sort_values(["repo", "category_priority", "score", "file"], ascending=[True, True, False, True])
        .groupby(["repo", "category"], as_index=False)
        .head(2)
        .copy()
    )

    best_one_per_category = (
        best_per_category.sort_values(["repo", "category_priority", "score", "file"], ascending=[True, True, False, True])
        .groupby(["repo", "category"], as_index=False)
        .head(1)
        .copy()
    )
    best_one_per_category["manual_review_priority"] = best_one_per_category["category"].map(CATEGORY_PRIORITY)

    priority_queue = (
        best_one_per_category.sort_values(["repo", "manual_review_priority", "score"], ascending=[True, True, False])
        .groupby("repo", as_index=False)
        .head(args.max_files_per_repo)
        .copy()
    )
    priority_queue["review_order_in_repo"] = priority_queue.groupby("repo").cumcount() + 1
    # priority_queue["manual_label"] = ""
    # priority_queue["comments"] = ""
    # priority_queue = priority_queue[["repo", "review_order_in_repo", "category", "file", "confidence", "score"]]

    priority_queue["manual_label"] = ""
    priority_queue["comments"] = ""

    priority_queue = priority_queue.rename(
        columns={"file": "evidence_path"}
    )

    priority_queue = priority_queue[
        [
            "repo",
            "review_order_in_repo",
            "category",
            "evidence_path",
            "confidence",
            "score",
            "manual_label",
            "comments",
        ]
    ]

    repo_summary_rows = []
    for item in data:
        repo = item["repo"]
        present_categories = [category for category in CATEGORIES if item.get("evidence", {}).get(category)]
        selected = priority_queue[priority_queue["repo"] == repo]
        repo_summary_rows.append(
            {
                "repo": repo,
                "categories_detected": ", ".join(present_categories),
                "files_to_check": len(selected),
                "high_confidence": int((selected["confidence"] == "high").sum()),
                "medium_confidence": int((selected["confidence"] == "medium").sum()),
                "low_or_worse": int(selected["confidence"].isin(["low", "very_low"]).sum()),
            }
        )

    repo_summary = pd.DataFrame(repo_summary_rows).sort_values(["low_or_worse", "repo"], ascending=[False, True])

    category_health = (
        df.groupby("category")
        .agg(
            repos=("repo", "nunique"),
            candidate_files=("file", "count"),
            avg_score=("score", "mean"),
            high_confidence=("confidence", lambda s: int((s == "high").sum())),
            medium_confidence=("confidence", lambda s: int((s == "medium").sum())),
            low_or_worse=("confidence", lambda s: int(s.isin(["low", "very_low"]).sum())),
        )
        .reset_index()
        .sort_values("avg_score", ascending=False)
    )

    heuristic_report = {
        "input_json": str(input_path),
        "repositories_in_input": int(df["repo"].nunique()),
        "candidate_rows": int(len(df)),
        "max_files_per_repo": int(args.max_files_per_repo),
        "categories": CATEGORIES,
        "note": "Heuristic scores are intended only for review prioritization and must not be used as final evidence.",
    }

    priority_queue.to_csv(output_dir / "tables" / "validated_priority_review_queue.csv", index=False)
    best_per_category[["repo", "category", "file", "confidence", "score"]].to_csv(
        output_dir / "tables" / "top2_per_category.csv", index=False
    )
    repo_summary.to_csv(output_dir / "tables" / "repo_review_summary.csv", index=False)
    category_health.to_csv(output_dir / "tables" / "category_health.csv", index=False)

    with (output_dir / "json" / "heuristic_report.json").open("w", encoding="utf-8") as handle:
        json.dump(heuristic_report, handle, indent=2)

    print(f"Files written to: {output_dir}")


if __name__ == "__main__":
    main()
