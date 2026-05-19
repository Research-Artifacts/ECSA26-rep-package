# Analysis Pipeline

This directory contains the datasets, scripts, and generated outputs associated with the analytical stage of the study. The artifacts provided here support the quantitative and qualitative analyses reported in the paper, including descriptive statistics, capability distribution analysis, architectural documentation assessment, and inter-rater agreement calculations.

The analysis pipeline was designed to support:

* transparency of analytical procedures;
* traceability between datasets, scripts, and outputs;
* reproducibility of generated tables and figures; and
* reuse of the analytical workflow in future replications or extensions.

---

# Directory Structure

```text
.
├── dataset/      -> curated datasets used during analysis
├── output/       -> generated outputs, tables, charts, and reports
└── scripts/      -> analysis and processing scripts
```

---

# Analysis Workflow

The analytical workflow implemented in this directory follows the sequence below:

1. Preparation of curated datasets
2. Quantitative analysis and aggregation
3. Capability-oriented analysis
4. Architectural documentation scanning
5. Inter-rater agreement computation
6. Generation of tables, charts, and derived outputs

---

# Dataset

The `dataset/` directory contains the curated datasets used as input for the analytical scripts.

| File                           | Description                                                                |
| ------------------------------ | -------------------------------------------------------------------------- |
| `study_corpus.csv`             | Final curated corpus used during the study                                 |
| `irr_capabilities.csv`         | Capability coding dataset used for inter-rater agreement analysis          |
| `irr_quality_requirements.csv` | Quality requirement coding dataset used for inter-rater agreement analysis |

These datasets represent the primary analytical inputs used throughout the study pipeline.

---

# Scripts

The `scripts/` directory contains the executable components responsible for generating the analytical outputs.

## Structure

```text
scripts/
├── kappa/    -> inter-rater agreement analysis
├── scan/     -> architectural documentation scanning
└── stats/    -> statistical and distribution analysis
```

---

## Statistical Analysis Scripts

| Script                     | Purpose                                               |
|----------------------------|-------------------------------------------------------|
| `quantitative_analyzer.py` | Generates descriptive and quantitative summaries      |
| `capability_analyzer.py`   | Computes capability distributions and related outputs |

---

## Inter-Rater Agreement Scripts

| Script                | Purpose                                                 |
|-----------------------|---------------------------------------------------------|
| `capability_kappa.py` | Computes agreement metrics for capability coding        |
| `quality_kappa.py`    | Computes agreement metrics for quality attribute coding |

---

## Architectural Documentation Scanning

| Script                    | Purpose                                                            |
|---------------------------|--------------------------------------------------------------------|
| `scan_arch_docs.py`       | Scans repositories for architecture-related documentation evidence |
| `build_priority_queue.py` | Generates prioritization artifacts for manual review support       |

Additional details are available in:

```text
scripts/scan/README.md
```

---

# Output

The `output/` directory contains all generated artifacts produced during the analytical workflow.

## Structure

```text
output/
├── charts/   -> generated figures and visualizations
├── json/     -> machine-readable reports
├── kappa/    -> inter-rater agreement outputs
└── tables/   -> generated analytical tables
```

---

# Charts

The `charts/` directory contains publication-oriented visualizations generated from the study datasets.

Examples include:

* domain distributions;
* capability distributions;
* quality attribute distributions;
* search-term distributions; and
* architectural documentation summaries.

---

# Tables

The `tables/` directory contains structured analytical outputs generated during the study.

Key outputs include:

* descriptive statistics;
* normalized datasets;
* capability summaries;
* review prioritization artifacts;
* repository classification summaries; and
* architectural documentation evidence tables.

---

# Kappa Outputs

The `kappa/` directory contains inter-rater agreement artifacts and derived statistical outputs.

These files include:

* pairwise agreement summaries;
* capability-oriented agreement reports;
* quality attribute agreement reports; and

---

# JSON Reports

The `json/` directory contains machine-readable reports generated during automated analysis and repository scanning procedures.

These reports support:

* reproducibility;
* traceability;
* automated inspection; and
* downstream analytical reuse.

---

# Reproducing the Main Outputs

The primary outputs can be regenerated by executing the scripts in the order below.

## Quantitative Analysis

```bash
cd scripts/stats

python quantitative_analyzer.py
python capability_analyzer.py
```

---

## Inter-Rater Agreement Analysis

```bash
cd scripts/kappa

python capability_kappa.py
python quality_kappa.py
```

---

## Architectural Documentation Scan

```bash
cd scripts/scan

python scan_arch_docs.py
python build_priority_queue.py
```

---

# Traceability Support

This directory was organized to maintain explicit traceability between:

* curated datasets;
* analysis scripts;
* generated outputs; and
* reported findings.

The structure aims to facilitate:

* methodological inspection;
* independent replication;
* result verification; and
* extension of the analytical workflow.

---

# Notes

Some outputs may depend on:

* execution order;
* external repository availability; or
* local environment configuration.

Please refer to the root-level installation and reproducibility documentation for environment setup and dependency management.
