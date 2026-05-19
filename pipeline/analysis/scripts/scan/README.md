# EdgeAI RQ3 Replication Package

This package rebuilds the evidence base for **RQ3 – Architectural Documentation of Edge AI Systems**.

It implements a reproducible pipeline with four stages:

1. **Prepare repository list** (`repos.csv`)
2. **Clone or update repositories** (`download_repos.py`)
3. **Scan repositories for architecture-documentation evidence** (`scan_arch_docs.py`)
4. **Generate manual checklist and project-level summary** (`build_manual_checklist.py`, `summarize_arch_docs.py`)

The pipeline is designed for studies in which architecture-relevant documentation is inferred from repository artifacts such as:

- overview documents (`README.md`, `docs/*.md`)
- diagrams and architecture/design folders
- ADRs and decision records
- deployment artifacts (`Dockerfile`, `docker-compose`, Helm, K8s manifests)
- interface contracts (`.proto`, OpenAPI, Swagger, AsyncAPI)
- evaluation artifacts (benchmark, performance, test, profiling)

## Recommended workflow

### 1) Create the repository list

Create a CSV file with at least these columns:

```csv
repo,repo_url
kubeedge,https://github.com/kubeedge/kubeedge.git
thin-edge.io,https://github.com/thin-edge/thin-edge.io.git
```

An optional third column can be used to pin a branch:

```csv
repo,repo_url,branch
kubeedge,https://github.com/kubeedge/kubeedge.git,master
```

### 2) Clone or update repositories

```bash
python download_repos.py \
  --input ../../dataset/repositories.csv \
  --workspace ./workspace \
  --depth 1
```

### 3) Scan architectural documentation evidence

```bash
python scan_arch_docs.py \
  --workspace ./workspace \ # Folder containing repositories
  --output-dir ../../outputs # Output directory
```

This produces:

- `arch_doc_scan_raw.json` – repository-level raw evidence
- `arch_doc_scan_project_summary.csv` – one row per repository
- `arch_doc_scan_evidence.csv` – one row per evidence path


### 4) Prioritize candidate evidence for manual validation

The following script generates a prioritized review queue from the raw architectural documentation scan results. 
Candidate files are ranked using heuristic scoring based on architecture-related patterns to support manual inspection 
and reduce validation effort.


```bash
python build_priority_queue.py \
  --input ../../outputs/json/arch_doc_scan_raw.json \
  --output-dir ../../outputs/tables/
```

After generation, reviewers manually inspect the prioritized evidence files and assign labels such as:

* `TP` (True Positive)
* `FP` (False Positive)
* `UNCLEAR`

The validated review queue is then used as input for the final project-level aggregation step.

### 5) Build project-level summary for the paper

```bash
python summarize_arch_docs.py \
  --input ../../outputs/validated_priority_review_queue.csv \
  --output-dir ../../outputs/
```

This produces:

- `project_presence.csv`
- `category_distribution.csv`
- `validation_report.json`

## Coding logic

The scanner is intentionally conservative. It does **not** claim that a file is a formal architecture description. Instead, it records **architecture-relevant documentary evidence** that may later be validated manually.

Categories used in this package:

- `arch_overview`
- `context`
- `views`
- `adrs`
- `deployment`
- `interface`
- `evaluation`
- `quality`
- `stakeholders`

## Suggested reporting rule

For RQ3, prefer **project-level presence** over raw file counts.

Example:

> “A repository was counted in category X if at least one validated artifact of category X was identified.”

This avoids over-weighting repositories containing many configuration files.

## Notes

- The scanner performs heuristic detection and should be combined with manual validation.
- The `manual_label` field accepts: `TP`, `FP`, `UNCLEAR`.
- Repositories can belong to multiple categories.
