# Inter-Rater Reliability (IRR) Analysis

This directory documents the inter-rater reliability (IRR) procedures adopted in the study for the structured 
classification activities associated with **RQ1** and **RQ4**.

In the paper, we report only the aggregate reliability indicators to preserve space and maintain narrative flow. This 
supplementary material provides the expanded results and the corresponding analysis files used to support those 
summaries.

## Scope of the IRR procedures

The IRR analysis was applied only to the research questions that required **explicit structured classification rules** 
beyond open coding:

**RQ1**: _classification of capability-related evidence according to the adopted capability groups._

`What quantitative distribution patterns emerge in open-source Edge AI-based systems with respect to ISO/IEC 30141 
capabilities, application domains, and project types?` 


**RQ4**: _classification of quality-related evidence according to the adopted quality attributes._

`What quality requirements are considered when architecting Edge AI-based Systems?`


These procedures were designed to assess the consistency of independent coding decisions before consolidation of the 
final classifications reported in the study.

## RQ1 — Capability classification reliability

For the capability-oriented classification procedure, three raters independently assessed the capability assignments 
under the adopted classification scheme.

### Summary

| Item                        |                                Value |
|-----------------------------|-------------------------------------:|
| Input file                  | `../../dataset/irr_capabilities.csv` |
| Output directory            |                `../../results/kappa` |
| Number of capability groups |                                    3 |
| Rater labels                |                           R1, R2, R3 |
| Overall macro kappa         |                           **0.8714** |

The overall macro Cohen’s kappa for this procedure was **0.8714**, indicating strong agreement among raters for the 
capability classification task.

### Pairwise kappa by capability group

| Capability group |  N | R1 vs R2 | R1 vs R3 | R2 vs R3 |
|------------------|---:|---------:|---------:|---------:|
| capability_1     | 99 |   0.7517 |   0.7766 |   0.8780 |
| capability_2     | 99 |   0.8820 |   0.9302 |   0.9008 |
| capability_3     | 99 |   0.8790 |   0.9303 |   0.9136 |

### Related files

*  [analysis_summary_capability_kappa.csv](../../pipeline/analysis/output/kappa/analysis_summary_capability_kappa.csv)  — overall summary statistics for the capability IRR analysis
*  [capability_kappa_long_format.csv](../../pipeline/analysis/output/kappa/capability_kappa_long_format.csv) — long-format pairwise kappa values
*  [capability_kappa_summary.csv](../../pipeline/analysis/output/kappa/capability_kappa_summary.csv) — summarized capability agreement results
*  [kappa_by_capability.csv](../../pipeline/analysis/output/kappa/kappa_by_capability.csv) — pairwise kappa values by capability group

## RQ4 — Quality classification reliability

For the quality-oriented classification procedure, three raters independently labeled the extracted architectural 
fragments according to the adopted quality attributes.

### Summary

| Item                             |                                        Value |
|----------------------------------|---------------------------------------------:|
| Input file                       | `../../dataset/irr_quality_requirements.csv` |
| Output directory                 |                        `../../results/kappa` |
| Number of fragments              |                                          400 |
| Number of detected attributes    |                                            9 |
| Rater 1 label                    |                                           R1 |
| Rater 2 label                    |                                           R2 |
| Rater 3 label                    |                                           R3 |
| Overall macro kappa              |                                   **0.8493** |
| Overall macro observed agreement |                                   **0.9741** |
| Overall exact set agreement      |                                   **0.8617** |
| Overall mean Jaccard similarity  |                                   **0.9051** |

The overall macro Cohen’s kappa for the quality classification procedure was **0.8493**, again indicating strong 
agreement. Because this task involved multi-label assignments, we also report complementary agreement measures, namely 
**observed agreement**, **exact set agreement**, and **mean Jaccard similarity**, to provide a more complete view of 
coder consistency.

### Pairwise kappa by quality attribute

| Quality attribute         |   R1 vs R2 |   R1 vs R3 |   R2 vs R3 |
|---------------------------|-----------:|-----------:|-----------:|
| Compatibility             |     0.8611 |     0.8155 |     0.9369 |
| Flexibility               |     0.8735 |     0.8274 |     0.9086 |
| Functional Suitability    |     0.7412 |     0.8201 |     0.8617 |
| Interaction Capability    |     0.7895 |     0.8573 |     0.8549 |
| Maintainability           |     0.8970 |     0.8423 |     0.8666 |
| Performance Efficiency    |     0.8881 |     0.8468 |     0.8731 |
| Reliability               |     0.8775 |     0.8842 |     0.9225 |
| Safety                    |     0.4981 |     0.4981 |     1.0000 |
| Security                  |     0.9558 |     0.9558 |     0.9771 |
| **Overall macro average** | **0.8202** | **0.8164** | **0.9113** |

### Related files

*  [analysis_summary_quality_kappa.csv](../../pipeline/analysis/output/kappa/analysis_summary_quality_kappa.csv) — overall summary statistics for the quality IRR analysis
*  [quality_kappa_by_attribute.csv](../../pipeline/analysis/output/kappa/quality_kappa_by_attribute.csv) — pairwise kappa values by quality attribute
*  [quality_kappa_long_format.csv](../../pipeline/analysis/output/kappa/quality_kappa_long_format.csv) — long-format agreement results
*  [quality_kappa_pair_summary.csv](../../pipeline/analysis/output/kappa/quality_kappa_pair_summary.csv) — summarized pairwise agreement statistics
*  [quality_multilabel_binary_matrix.csv](../../pipeline/analysis/output/kappa/quality_multilabel_binary_matrix.csv) — binary matrix used to represent multi-label quality assignments

## Notes on interpretation

The results reported here are intended to document the consistency of the structured classification procedures used in 
the study. They should be interpreted together with the methodological description in the paper, where the 
classification rules, adjudication logic, and analytical role of each coded dataset are described.
