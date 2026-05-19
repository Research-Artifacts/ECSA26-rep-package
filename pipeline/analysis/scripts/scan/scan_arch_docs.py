#!/usr/bin/env python3
"""Scan repositories for architecture-documentation evidence for RQ3.

This script is part of the replication package for the empirical study on
Edge AI repositories. Its goal is to identify repository artifacts that may
contain architecture-related documentation, such as overviews, diagrams, ADRs,
deployment notes, interface specifications, evaluation material, and other
artifacts relevant to architectural analysis.

The scanner is intentionally heuristic and conservative. It is designed to
prioritize candidate evidence for manual review, not to produce final labels.
As a result, the generated outputs should always be validated by a human
reviewer before being used in the study analysis.

Expected input
--------------
- A workspace directory containing the cloned repositories to be scanned.

Generated outputs
-----------------
- arch_doc_scan_raw.json:
  Repository-level scan results with all detected evidence.
- arch_doc_scan_project_summary.csv:
  One row per repository, summarizing detected categories.
- arch_doc_scan_evidence.csv:
  One row per evidence path, useful for inspection and follow-up review.

Usage
-----
Run the script from the command line, pointing it to the repository workspace
and an output directory:

    python scan_arch_docs.py \
        --workspace /path/to/cloned_repositories \
        --output-dir /path/to/output

Optional:
    --verbose
        Enable debug-level logging for a more detailed scan trace.

Example
-------
    python scan_arch_docs.py \
        --workspace ../../repositories \
        --output-dir ../../output

Notes
-----
- The scan skips common build, cache, vendor, and version-control directories.
- Text files and diagram-like artifacts are checked using filename, directory,
  and content heuristics.
- The outputs are intended for replication transparency and manual prioritization.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable, Optional

ARCH_DOC_SCAN_RAW_JSON = "arch_doc_scan_raw.json"
ARCH_DOC_SCAN_PROJECT_SUMMARY_CSV = "arch_doc_scan_project_summary.csv"
ARCH_DOC_SCAN_EVIDENCE_CSV = "arch_doc_scan_evidence.csv"

LOGGER = logging.getLogger("scan_arch_docs")

TEXT_EXTS = {".md", ".mdx", ".txt", ".rst", ".adoc", ".yaml", ".yml", ".json", ".toml", ".ini", ".proto", ".api"}
DIAGRAM_EXTS = {".puml", ".plantuml", ".drawio", ".mmd", ".mermaid", ".svg", ".png", ".jpg", ".jpeg", ".webp"}
SKIP_DIRS = {
    ".git", ".hg", ".svn", ".idea", ".vscode", "__pycache__", "node_modules",
    "build", "dist", "target", ".mypy_cache", ".pytest_cache"
}
VENDOR_DIRS = {"vendor", "third_party", "thirdparty", "deps", "external", "externals", "site-packages"}

CATEGORIES = [
    "arch_overview", "context", "views", "adrs", "deployment",
    "interface", "evaluation", "quality", "stakeholders"
]

FILE_NAME_RULES: dict[str, list[re.Pattern[str]]] = {
    "arch_overview": [
        re.compile(r"^(architecture|software[-_ ]?architecture|system[-_ ]?architecture)(\..+)?$", re.I),
        re.compile(r"^(design[-_ ]?overview|architecture[-_ ]?overview)(\..+)?$", re.I),
    ],
    "context": [
        re.compile(r"^(system[-_ ]?context|context[-_ ]?diagram)(\..+)?$", re.I),
    ],
    "views": [
        re.compile(r"^(logical[-_ ]?view|deployment[-_ ]?view|component[-_ ]?diagram|container[-_ ]?diagram|c4.*)(\..+)?$", re.I),
    ],
    "adrs": [
        re.compile(r"^adr[-_ ]?\d+.*\.(md|rst|txt)$", re.I),
        re.compile(r"^\d{3,4}[-_ ].*\.(md|rst|txt)$", re.I),
    ],
    "interface": [
        re.compile(r"^(openapi|swagger|asyncapi|proto|api[-_ ]?spec|interface)(\..+)?$", re.I),
    ],
    "evaluation": [
        re.compile(r"^(benchmark|benchmarks|profiling|performance|evaluation|atam|trade[-_ ]?off)(\..+)?$", re.I),
    ],
    "quality": [
        re.compile(r"^(quality|quality[-_ ]?attributes|nfr|non[-_ ]?functional)(\..+)?$", re.I),
    ],
    "stakeholders": [
        re.compile(r"^(stakeholders?|stakeholder[-_ ]?analysis|viewpoints?)(\..+)?$", re.I),
    ],
}

DIR_HINTS: dict[str, list[str]] = {
    "adrs": ["adr", "adrs", "decisions", "decision-records"],
    "deployment": ["deploy", "deployment", "k8s", "kubernetes", "helm", "manifests", "docker"],
    "evaluation": ["benchmark", "benchmarks", "perf", "performance", "profiling", "evaluation", "tests"],
    "views": ["architecture", "arch", "design", "diagrams", "views"],
}

CONTENT_RULES: dict[str, list[re.Pattern[str]]] = {
    "arch_overview": [
        re.compile(r"\barchitecture\b", re.I),
        re.compile(r"\bcomponent(s)?\b", re.I),
        re.compile(r"\bdeployment\b", re.I),
    ],
    "context": [
        re.compile(r"\bsystem context\b", re.I),
        re.compile(r"\bexternal actors?\b", re.I),
        re.compile(r"\bupstream\b|\bdownstream\b", re.I),
    ],
    "views": [
        re.compile(r"\bc4\b", re.I),
        re.compile(r"\blogical view\b", re.I),
        re.compile(r"\bdeployment view\b", re.I),
        re.compile(r"\bcomponent diagram\b|\bsequence diagram\b", re.I),
    ],
    "adrs": [
        re.compile(r"\barchitecture decision record\b", re.I),
        re.compile(r"\bstatus:\s*(accepted|proposed|rejected|superseded)\b", re.I),
    ],
    "deployment": [
        re.compile(r"\bdocker\b", re.I),
        re.compile(r"\bkubernetes\b|\bk8s\b", re.I),
        re.compile(r"\bhelm\b", re.I),
        re.compile(r"\bdeployment\b", re.I),
    ],
    "interface": [
        re.compile(r"\bopenapi\b|\bswagger\b|\basyncapi\b", re.I),
        re.compile(r"\bproto3\b|\bgrpc\b", re.I),
        re.compile(r"\bapi\b", re.I),
    ],
    "evaluation": [
        re.compile(r"\bbenchmark\b|\bthroughput\b|\blatency\b", re.I),
        re.compile(r"\bprofile\b|\bprofiling\b", re.I),
        re.compile(r"\bperformance\b", re.I),
    ],
    "quality": [
        re.compile(r"\bquality attributes?\b", re.I),
        re.compile(r"\bnon[- ]?functional\b|\bnfr\b", re.I),
        re.compile(r"\breliability\b|\bavailability\b|\bsecurity\b|\bmaintainability\b", re.I),
    ],
    "stakeholders": [
        re.compile(r"\bstakeholders?\b", re.I),
        re.compile(r"\bconcerns?\b", re.I),
        re.compile(r"\bviewpoints?\b", re.I),
    ],
}


@dataclass
class RepoScanResult:
    repo: str
    repo_path: str
    evidence: dict[str, list[str]] = field(default_factory=lambda: {category: [] for category in CATEGORIES})

    def add(self, category: str, path: str) -> None:
        if path not in self.evidence[category]:
            self.evidence[category].append(path)

    @property
    def flags(self) -> dict[str, bool]:
        return {f"has_{category}": bool(paths) for category, paths in self.evidence.items()}

    @property
    def evidence_count(self) -> int:
        return sum(len(paths) for paths in self.evidence.values())


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s | %(levelname)s | %(message)s")


def should_skip(path: Path) -> bool:
    parts = {part.lower() for part in path.parts}
    return bool(parts & SKIP_DIRS) or bool(parts & VENDOR_DIRS)


def read_head(path: Path, max_bytes: int = 20000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:max_bytes]
    except Exception:
        return ""


def file_name_matches(file_name: str) -> set[str]:
    matched: set[str] = set()
    for category, patterns in FILE_NAME_RULES.items():
        if any(pattern.match(file_name) for pattern in patterns):
            matched.add(category)
    return matched


def dir_hint_matches(path: Path) -> set[str]:
    matched: set[str] = set()
    lowered_parts = [part.lower() for part in path.parts]
    for category, hints in DIR_HINTS.items():
        if any(hint in lowered_parts for hint in hints):
            matched.add(category)
    return matched


def content_matches(text: str) -> set[str]:
    matched: set[str] = set()
    for category, patterns in CONTENT_RULES.items():
        hits = sum(1 for pattern in patterns if pattern.search(text))
        if hits >= 1:
            matched.add(category)
    return matched


def is_deployment_artifact(path: Path) -> bool:
    name = path.name.lower()
    path_str = str(path).lower()
    if name == "dockerfile":
        return True
    if name in {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml", "chart.yaml"}:
        return True
    if any(token in path_str for token in ["k8s", "kubernetes", "helm", "deployment", "manifests"]):
        if path.suffix.lower() in {".yaml", ".yml", ".json", ".tpl"}:
            return True
    return False


def is_interface_artifact(path: Path) -> bool:
    name = path.name.lower()
    return path.suffix.lower() == ".proto" or name in {"openapi.yaml", "openapi.yml", "swagger.yaml", "swagger.yml", "asyncapi.yaml", "asyncapi.yml"}


def is_diagram_candidate(path: Path) -> bool:
    return path.suffix.lower() in DIAGRAM_EXTS


def scan_repository(repo_dir: Path) -> RepoScanResult:
    result = RepoScanResult(repo=repo_dir.name, repo_path=str(repo_dir))

    for path in repo_dir.rglob("*"):
        if should_skip(path):
            continue
        if not path.is_file():
            continue

        rel_path = str(path.relative_to(repo_dir))
        name_matches = file_name_matches(path.name)
        dir_matches = dir_hint_matches(path.parent)

        for category in name_matches | dir_matches:
            if category == "views" and path.name.lower() == "views.py":
                continue
            result.add(category, rel_path)

        if is_deployment_artifact(path):
            result.add("deployment", rel_path)

        if is_interface_artifact(path):
            result.add("interface", rel_path)

        if is_diagram_candidate(path):
            if any(part.lower() in {"architecture", "arch", "design", "diagrams", "docs"} for part in path.parts):
                result.add("views", rel_path)

        if path.suffix.lower() in TEXT_EXTS or path.name.lower() == "dockerfile":
            text = read_head(path)
            if not text:
                continue
            for category in content_matches(text):
                result.add(category, rel_path)

    return result


def write_json(results: list[RepoScanResult], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    serializable = []
    for result in results:
        serializable.append(
            {
                "repo": result.repo,
                "repo_path": result.repo_path,
                "flags": result.flags,
                "evidence_count": result.evidence_count,
                "evidence": result.evidence,
            }
        )
    output_path.write_text(json.dumps(serializable, indent=2, ensure_ascii=False), encoding="utf-8")


def write_project_summary(results: list[RepoScanResult], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["repo", "repo_path", "evidence_count", *[f"has_{category}" for category in CATEGORIES]]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            row = {"repo": result.repo, "repo_path": result.repo_path, "evidence_count": result.evidence_count}
            row.update(result.flags)
            writer.writerow(row)


def write_evidence_rows(results: list[RepoScanResult], output_path: Path) -> None:
    fieldnames = ["repo", "category", "evidence_path"]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            for category, paths in result.evidence.items():
                for evidence_path in sorted(paths):
                    writer.writerow({"repo": result.repo, "category": category, "evidence_path": evidence_path})

def looks_like_repo_dir(path: Path) -> bool:
    if not path.is_dir():
        return False

    if (path / ".git").exists():
        return True

    likely_markers = [
        "README.md", "readme.md", "Dockerfile", "docker-compose.yml",
        "docker-compose.yaml", "pyproject.toml", "package.json",
        "go.mod", "Cargo.toml", ".github"
    ]

    return any((path / marker).exists() for marker in likely_markers)


def iter_repo_dirs(workspace: Path) -> Iterable[Path]:
    for child in sorted(workspace.iterdir()):
        if looks_like_repo_dir(child):
            yield child
            


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan repository corpus for architecture-documentation evidence.")
    parser.add_argument("--workspace", required=True, help="Directory containing cloned repositories.")
    parser.add_argument("--output-dir", required=True, help="Directory where outputs will be written.")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    setup_logging(args.verbose)

    workspace = Path(args.workspace).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    results: list[RepoScanResult] = []
    repo_dirs = list(iter_repo_dirs(workspace))
    LOGGER.info("Scanning %d repositories", len(repo_dirs))

    for repo_dir in repo_dirs:
        LOGGER.info("Scanning %s", repo_dir.name)
        results.append(scan_repository(repo_dir))


    write_json(results, output_dir / "json" / ARCH_DOC_SCAN_RAW_JSON)
    write_project_summary(results, output_dir/ "tables" / ARCH_DOC_SCAN_PROJECT_SUMMARY_CSV)
    write_evidence_rows(results, output_dir / "tables"/ ARCH_DOC_SCAN_EVIDENCE_CSV)

    LOGGER.info("Done. Outputs written to %s", output_dir)


if __name__ == "__main__":
    main()
