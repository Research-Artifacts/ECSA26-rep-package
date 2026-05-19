# Replication Package

Supplementary material and replication package for the study:

## *Open-Source Edge AI Systems in Practice: An Empirical Study of Architectural Characteristics*

**Authors:** 

[Jander Pereira Santos Junior](https://orcid.org/0009-0008-0320-0530)

[Luana Martins](https://orcid.org/0000-0001-6340-7615)

[Paulo Anselmo da Mota Silveira Neto](https://orcid.org/0000-0003-0197-8249)

[Eduardo Santana de Almeida](https://orcid.org/0000-0002-9312-6715)

_Submitted to the European Conference on Software Architecture (ECSA 2026)_

---

# Abstract

Edge AI-based systems distribute intelligence across heterogeneous, resource-constrained environments along the 
continuum. Despite growing adoption, their architectural practices remain poorly consolidated in open-source software, 
and the label `Edge AI` is often applied to artifacts with uneven architectural relevance.

This paper reports an empirical study of open-source GitHub repositories identified through repository mining and 
analyzed through qualitative coding informed by **ISO/IEC 30141**, **ISO/IEC/IEEE 42010**, and **ISO/IEC 25010**. We examine 
capability distributions, architectural patterns, documentation practices, and architecturally relevant quality concerns.

The results show a predominance of supporting, interface, and data capabilities, with most systems emphasizing 
infrastructure-oriented and cross-layer concerns across device, edge, fog, and cloud environments. Architectural 
knowledge is documented mainly through executable and operational artifacts, such as configuration, interface, and 
deployment files, rather than explicit architecture descriptions. Quality concerns are strongly runtime-centered, 
especially reliability, maintainability, and performance efficiency, while concerns such as safety assurance and energy 
awareness appear only marginally.

These findings expose recurring blind spots in open-source Edge AI practice and provide an empirical basis for future 
architectural guidance and evaluation.

---
# Overview

This repository contains the complete supplementary material and replication package associated with our empirical study 
on architectural practices in **Edge AI–based systems**.

The package was designed to support:
- transparency of the research process;
- traceability between evidence, scripts, and findings;
- methodological inspection;
- reproducibility of analytical outputs; and
- reuse and extension of the study artifacts.

The repository includes:
- repository collection and preprocessing pipelines;
- curated analytical datasets;
- qualitative coding and adjudication artifacts;
- executable analysis scripts;
- generated tables and visualizations; and
- traceability-oriented supporting material.

The repository structure was organized to facilitate:
- repeatability;
- independent inspection;
- partial reproducibility; and
- future study extensions.
---

# Quick Reproduction

The primary analytical outputs reported in the study can be reproduced using the following steps.

## 1. Install Dependencies

```bash
pip install -r docs/requirements.txt
```

Additional setup instructions are available in:


[INSTALL.md](INSTALL.md)

---

## 2. Reproducing the Study

The executable workflows associated with repository collection, preprocessing, and analytical processing are organized 
under the [pipeline](pipeline) directory.

### Collection Pipeline

The repository discovery and preprocessing workflow are documented in:

**[README.md](pipeline/collection/README.md)**

This includes:

* repository mining;
* preprocessing steps;
* raw dataset generation; and
* repository retrieval procedures.

---

### Analysis Pipeline

The analytical workflow is documented in:

**[README.md](pipeline/analysis/README.md)**

This includes:

* dataset preparation;
* statistical analysis;
* agreement computation;
* architectural documentation scanning; and
* generation of figures and tables.


## 3. Generated Outputs

Generated artifacts will be available in:

```text
pipeline/analysis/output/
```

This directory contains:

* tables;
* charts;
* agreement statistics;
* machine-readable reports; and
* derived analytical artifacts.

---

# Repository Structure

```text
.
├── artifacts/     -> methodological and qualitative study artifacts
├── docs/          -> supporting documentation and dependencies
├── pipeline/      -> collection and analytical processing pipelines
├── INSTALL.md     -> installation and environment setup
├── LICENSE        -> repository license
└── README.md
```

---

# Repository Organization

The repository is organized into three main conceptual areas:

| Directory    | Purpose                                                 |
| ------------ | ------------------------------------------------------- |
| `artifacts/` | Qualitative, methodological, and traceability artifacts |
| `pipeline/`  | Executable collection and analysis workflows            |
| `docs/`      | Supporting documentation and dependency specifications  |

---

# Artifacts

The `artifacts/` directory contains the primary methodological and qualitative artifacts used throughout the study.

## Structure

```text
artifacts/
├── coding/
├── evidence/
├── screening/
├── statistics/
├── taxonomy/
└── workbook/
```

---

## Coding Artifacts

Contains methodological artifacts related to:
- qualitative coding procedures;
- adjudication activities; and
- inter-rater agreement documentation.

Key files:
- [irr_agreement.md](artifacts/coding/irr_agreement.md)

---

## Evidence Artifacts

Contains manually reviewed and curated evidence artifacts used during the architecture-oriented assessment.

Key files:

* [all_collected_fragments.csv](artifacts/evidence/all_collected_fragments.csv)
* [selected_fragments.csv](artifacts/evidence/selected_fragments.csv)
* [manual_review_artifacts_ISO42010.csv](artifacts/evidence/manual_review_artifacts_ISO42010.csv)

---

## Screening Artifacts

Contains the screening and eligibility support material used during corpus selection.

Key files:

* [eligibility_criteria.md](artifacts/screening/eligibility_criteria.md)
* [included_repositories.csv](artifacts/screening/included_repositories.csv)

---

## Statistical Artifacts

Contains descriptive summaries regarding the empirical evidence base.

Key files:

* [empirical-evidence-statistics.md](artifacts/statistics/empirical-evidence-statistics.md)

---

## Taxonomy Artifacts

Contains conceptual classification and architectural synthesis artifacts.

Key files:

* [architectural_building_blocks.md](artifacts/taxonomy/architectural_building_blocks.md)
* [domain_taxonomy.csv](artifacts/taxonomy/domain_taxonomy.csv)

---

## Workbook

Contains the master operational spreadsheet used during the study execution.

Key file:

* [master_study_workbook.xlsx](artifacts/workbook/master_study_workbook.xlsx)

---

# Pipeline

The `pipeline/` directory contains the executable workflows responsible for:

* repository collection;
* preprocessing;
* dataset construction;
* analysis execution; and
* output generation.

## Structure

```text
pipeline/
├── collection/
└── analysis/
```

---

# Collection Pipeline

The `pipeline/collection/` directory contains the repository discovery and preprocessing workflow.

It includes:

* API-based repository search scripts;
* preprocessing utilities;
* raw search outputs;
* processed datasets; and
* repository retrieval support.

Additional details are available in:

[README.md](pipeline/collection/README.md)

---

# Analysis Pipeline

The `pipeline/analysis/` directory contains:

* curated datasets;
* analytical scripts;
* agreement analysis workflows;
* generated outputs; and
* publication-oriented artifacts.

## Main Components

| Directory   | Purpose                                |
|-------------|----------------------------------------|
| `dataset/`  | Curated analytical datasets            |
| `scripts/`  | Statistical and processing scripts     |
| `output/`   | Generated tables, charts, and reports  |

Additional details are available in:

[README.md](pipeline/analysis/README.md)

---

# Replication Workflow

The study workflow implemented in this repository follows the sequence below:

1. Repository discovery and retrieval
2. Dataset preprocessing and filtering
3. Eligibility screening
4. Fragment extraction
5. Manual coding and adjudication
6. Quantitative and qualitative analysis
7. Agreement computation
8. Figure and table generation
9. Result consolidation

---

# Traceability to Research Questions

| Research Question | Main Supporting Artifacts                                                                                                                                                                                                                                                         |
|-------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `[RQ1]`           | [capability_distribution.csv](pipeline/analysis/output/tables/capability_distribution.csv), [domain_distribution.csv](pipeline/analysis/output/tables/domain_distribution.csv), [project_type_distribution.csv](pipeline/analysis/output/tables/project_type_distribution.csv)    |
| `[RQ2]`           | [arch_doc_scan_evidence.csv](pipeline/analysis/output/tables/arch_doc_scan_evidence.csv), [priority_review_queue.csv](pipeline/analysis/output/tables/priority_review_queue.csv), [manual_review_artifacts_ISO42010.csv](artifacts/evidence/manual_review_artifacts_ISO42010.csv) |
| `[RQ3]`           | [architectural_building_blocks.md](artifacts/taxonomy/architectural_building_blocks.md)                                                                                                                                                                                           |
| `[RQ4]`           | [selected_fragments.csv](artifacts/evidence/selected_fragments.csv)                                                                                                                                                                                                               |

---

# Limitations

This replication package reflects the state of the analyzed repositories during the study execution period.

External factors such as:

* repository removal;
* repository evolution;
* metadata drift;
* API changes; or
* platform availability

may affect the exact reconstruction of the original corpus over time.

---

[//]: # (# Citation)

[//]: # ()
[//]: # (If you use this replication package, please cite:)

[//]: # ()
[//]: # (```bibtex id="7pt6zn")

[//]: # ([BIBTEX HERE])

[//]: # (```)

---
# License

This repository is distributed under the terms of the MIT License.

Third-party repositories, datasets, and external artifacts referenced or analyzed in this study remain subject to their respective original licenses.

See:

[LICENSE](LICENSE)