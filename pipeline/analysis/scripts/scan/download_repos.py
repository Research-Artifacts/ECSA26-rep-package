#!/usr/bin/env python3
"""Download or update the repository corpus for RQ2.

Input CSV columns:
- repo: logical repository name used in outputs
- repo_url: git clone URL
- branch: optional branch name

The script clones missing repositories and updates existing clones.
It is safe to rerun and is suitable for replication packages.
"""

from __future__ import annotations

import argparse
import csv
import logging
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class RepoSpec:
    repo: str
    repo_url: str
    branch: Optional[str] = None


LOGGER = logging.getLogger("download_repos")


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s | %(levelname)s | %(message)s")


def load_repo_specs(csv_path: Path) -> list[RepoSpec]:
    specs: list[RepoSpec] = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"repo", "repo_url"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
        for row in reader:
            repo = (row.get("repo") or "").strip()
            repo_url = (row.get("repo_url") or "").strip()
            branch = (row.get("branch") or "").strip() or None
            if not repo or not repo_url:
                continue
            specs.append(RepoSpec(repo=repo, repo_url=repo_url, branch=branch))
    return specs


def run_git(args: list[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd) if cwd else None,
        check=False,
        capture_output=True,
        text=True,
    )


def clone_repo(spec: RepoSpec, target_dir: Path, depth: int) -> None:
    cmd = ["clone", spec.repo_url, str(target_dir)]
    if depth > 0:
        cmd[1:1] = [f"--depth={depth}"]
    if spec.branch:
        cmd[1:1] = ["--branch", spec.branch, "--single-branch"]
    result = run_git(cmd)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to clone {spec.repo}: {result.stderr.strip()}")


def update_repo(target_dir: Path) -> None:
    # Conservative update strategy for replication packages.
    result = run_git(["fetch", "--all", "--tags", "--prune"], cwd=target_dir)
    if result.returncode != 0:
        raise RuntimeError(f"git fetch failed in {target_dir}: {result.stderr.strip()}")

    branch_result = run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=target_dir)
    if branch_result.returncode != 0:
        raise RuntimeError(f"Cannot resolve current branch in {target_dir}: {branch_result.stderr.strip()}")
    current_branch = branch_result.stdout.strip()

    reset_result = run_git(["reset", "--hard", f"origin/{current_branch}"], cwd=target_dir)
    if reset_result.returncode != 0:
        raise RuntimeError(f"git reset failed in {target_dir}: {reset_result.stderr.strip()}")

    clean_result = run_git(["clean", "-fd"], cwd=target_dir)
    if clean_result.returncode != 0:
        raise RuntimeError(f"git clean failed in {target_dir}: {clean_result.stderr.strip()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Clone or update the RQ1.3 repository corpus.")
    parser.add_argument("--input", required=True, help="CSV with repo and repo_url columns.")
    parser.add_argument("--workspace", required=True, help="Directory where repositories will be stored.")
    parser.add_argument("--depth", type=int, default=1, help="Clone depth. Use 0 for full history.")
    parser.add_argument("--reset-missing-git", action="store_true", help="Delete non-git folders and clone again.")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    setup_logging(args.verbose)

    input_path = Path(args.input).expanduser().resolve()
    workspace = Path(args.workspace).expanduser().resolve()
    workspace.mkdir(parents=True, exist_ok=True)

    specs = load_repo_specs(input_path)
    LOGGER.info("Loaded %d repositories from %s", len(specs), input_path)

    for spec in specs:
        target_dir = workspace / spec.repo
        try:
            if not target_dir.exists():
                LOGGER.info("Cloning %s", spec.repo)
                clone_repo(spec, target_dir, args.depth)
                continue

            git_dir = target_dir / ".git"
            if not git_dir.exists():
                if args.reset_missing_git:
                    LOGGER.warning("Removing non-git folder and recloning: %s", target_dir)
                    shutil.rmtree(target_dir)
                    clone_repo(spec, target_dir, args.depth)
                else:
                    LOGGER.warning("Skipping %s because %s is not a git repository", spec.repo, target_dir)
                continue

            LOGGER.info("Updating %s", spec.repo)
            update_repo(target_dir)
        except Exception as exc:
            LOGGER.error("Repository %s failed: %s", spec.repo, exc)

    LOGGER.info("Done.")


if __name__ == "__main__":
    main()
