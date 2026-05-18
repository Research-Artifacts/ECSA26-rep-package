#!/usr/bin/env python3
"""
RQ1.1 Capability Analysis Replication Script

Reads a capability CSV dataset, normalizes ISO/IEC 30141 capability families,
processes edge continuum layers, exports replication tables to CSV, and
generates publication-ready figures in PNG and PDF formats.

Design decisions:
- Heatmap uses multi-layer expansion to preserve cross-layer presence.
- Stacked bar uses a single primary layer to avoid double counting.
- All plots follow a unified soft blue/gray visual palette.

Example:
    python capability_analyzer.py \
        --input ../../dataset/study_corpus.csv \
        --output-dir ../../output/
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap


LAYER_ORDER = ["Device", "Edge", "Fog", "Cloud", "Cross-cutting"]
CAPABILITY_ORDER = ["Data", "Interface", "Supporting", "Transducer"]

SOFT_COLORS = {
    "Data": "#3b5b92",
    "Interface": "#6c8ebf",
    "Supporting": "#888888",
    "Transducer": "#b0b0b0",
}

HEATMAP_CMAP = LinearSegmentedColormap.from_list(
    "edge_blue_scale",
    ["#f5f7fb", "#dbe4f0", "#b9c9df", "#8aa6c8", "#5e7eab", "#3b5b92"],
)

plt.rcParams.update(
    {
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.labelsize": 11,
        "legend.fontsize": 10,
        "legend.title_fontsize": 10,
    }
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate replication tables and figures for ISO/IEC 30141 "
            "capability analysis across edge continuum layers."
        )
    )
    parser.add_argument("--input", required=True, help="Path to the input CSV file.")
    parser.add_argument(
        "--output-dir",
        default="results",
        help="Directory where outputs will be stored. Default: results",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="CSV encoding. Default: utf-8",
    )
    parser.add_argument(
        "--csv-separator",
        default=",",
        help="CSV field separator. Default: ','",
    )
    parser.add_argument(
        "--repo-col",
        default="repo_name",
        help="Repository name column. Default: repo_name",
    )
    parser.add_argument(
        "--layer-col",
        default="layer_caps",
        help="Layer column. Default: layer_caps",
    )
    parser.add_argument(
        "--capability-cols",
        nargs="+",
        default=["ISO_C1", "ISO_C2", "ISO_C3"],
        help="Capability columns in wide format. Default: ISO_C1 ISO_C2 ISO_C3",
    )
    parser.add_argument(
        "--title-prefix",
        default="",
        help="Optional prefix added to chart titles.",
    )
    return parser.parse_args()


def ensure_directories(base_dir: Path) -> tuple[Path, Path]:
    tables_dir = base_dir / "tables"
    charts_dir = base_dir / "charts"
    tables_dir.mkdir(parents=True, exist_ok=True)
    charts_dir.mkdir(parents=True, exist_ok=True)
    return tables_dir, charts_dir


def validate_columns(df: pd.DataFrame, columns: Iterable[str]) -> None:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(
            f"The following columns were not found in the CSV: {missing}. "
            f"Available columns: {list(df.columns)}"
        )


def normalize_capability_family(value: object) -> str | None:
    if pd.isna(value):
        return None

    text = str(value).strip().lower()
    if not text:
        return None

    rename_map = {
        "data capability": "Data",
        "data capabilities": "Data",
        "interface capability": "Interface",
        "interface capabilities": "Interface",
        "supporting capability": "Supporting",
        "supporting capabilities": "Supporting",
        "transducer capability": "Transducer",
        "transducer capabilities": "Transducer",
    }

    normalized = rename_map.get(text, text.title())
    if normalized not in CAPABILITY_ORDER:
        return normalized
    return normalized


def expand_layers(value: object) -> list[str]:
    """
    Preserves multi-layer presence for analyses such as the heatmap.
    Example:
        'edge-device' -> ['Device', 'Edge']
        'edge-fog' -> ['Edge', 'Fog']
        'continuum' -> ['Cross-cutting']
    """
    if pd.isna(value):
        return []

    text = str(value).strip().lower()
    if not text:
        return []

    if "continuum" in text:
        return ["Cross-cutting"]

    layers: list[str] = []
    if "device" in text:
        layers.append("Device")
    if "edge" in text:
        layers.append("Edge")
    if "fog" in text:
        layers.append("Fog")
    if "cloud" in text:
        layers.append("Cloud")

    return list(dict.fromkeys(layers))


def primary_layer(value: object) -> str | None:
    """
    Returns a single canonical layer for charts that must not double count.

    Rule:
    - if 'continuum' appears -> Cross-cutting
    - otherwise, chooses the left-most recognized layer in the original string

    Examples:
        'edge-device' -> Edge
        'device-edge' -> Device
        'fog-cloud' -> Fog
    """
    if pd.isna(value):
        return None

    text = str(value).strip().lower()
    if not text:
        return None

    if "continuum" in text:
        return "Cross-cutting"

    candidates = {
        "device": "Device",
        "edge": "Edge",
        "fog": "Fog",
        "cloud": "Cloud",
    }

    positions: list[tuple[int, str]] = []
    for token, label in candidates.items():
        pos = text.find(token)
        if pos != -1:
            positions.append((pos, label))

    if not positions:
        return None

    positions.sort(key=lambda item: item[0])
    return positions[0][1]


def build_long_dataset_multilayer(
    df: pd.DataFrame,
    repo_col: str,
    layer_col: str,
    capability_cols: list[str],
) -> pd.DataFrame:
    """
    Multi-layer dataset for analyses that intentionally represent presence
    across more than one layer.
    """
    working_df = df.copy()
    working_df["layer_list"] = working_df[layer_col].apply(expand_layers)
    working_df = working_df.explode("layer_list")
    working_df = working_df.dropna(subset=["layer_list"])

    frames: list[pd.DataFrame] = []
    for capability_col in capability_cols:
        frame = working_df[[repo_col, capability_col, "layer_list"]].rename(
            columns={
                repo_col: "repo_name",
                capability_col: "iso_family",
                "layer_list": "layer",
            }
        )
        frames.append(frame)

    long_df = pd.concat(frames, ignore_index=True)
    long_df["iso_family"] = long_df["iso_family"].apply(normalize_capability_family)
    long_df = long_df.dropna(subset=["iso_family", "layer"])
    return long_df.reset_index(drop=True)


def build_long_dataset_primary_layer(
    df: pd.DataFrame,
    repo_col: str,
    layer_col: str,
    capability_cols: list[str],
) -> pd.DataFrame:
    """
    Single-layer dataset for analyses that must avoid inflation,
    especially stacked bars.
    """
    working_df = df.copy()
    working_df["primary_layer"] = working_df[layer_col].apply(primary_layer)
    working_df = working_df.dropna(subset=["primary_layer"])

    frames: list[pd.DataFrame] = []
    for capability_col in capability_cols:
        frame = working_df[[repo_col, capability_col, "primary_layer"]].rename(
            columns={
                repo_col: "repo_name",
                capability_col: "iso_family",
                "primary_layer": "layer",
            }
        )
        frames.append(frame)

    long_df = pd.concat(frames, ignore_index=True)
    long_df["iso_family"] = long_df["iso_family"].apply(normalize_capability_family)
    long_df = long_df.dropna(subset=["iso_family", "layer"])
    return long_df.reset_index(drop=True)


def build_heatmap_counts(long_df: pd.DataFrame) -> pd.DataFrame:
    table = long_df.groupby(["iso_family", "layer"]).size().unstack(fill_value=0)
    table = table.reindex(index=CAPABILITY_ORDER, fill_value=0)
    table = table.reindex(columns=LAYER_ORDER, fill_value=0)
    return table


def build_heatmap_percent(counts_df: pd.DataFrame) -> pd.DataFrame:
    total = counts_df.to_numpy().sum()
    if total == 0:
        return counts_df.astype(float)
    return (counts_df / total * 100).round(2)


def build_capability_distribution(long_df: pd.DataFrame) -> pd.DataFrame:
    counts = long_df["iso_family"].value_counts()
    table = counts.rename_axis("iso_family").reset_index(name="count")

    total = int(table["count"].sum()) if not table.empty else 0
    if total > 0:
        table["percentage"] = (table["count"] / total * 100).round(2)
    else:
        table["percentage"] = 0.0

    table["iso_family"] = pd.Categorical(
        table["iso_family"],
        categories=CAPABILITY_ORDER,
        ordered=True,
    )
    table = table.sort_values("iso_family").reset_index(drop=True)
    table["iso_family"] = table["iso_family"].astype(str)
    return table


def save_csv(df: pd.DataFrame, path: Path, include_index: bool = True) -> None:
    df.to_csv(path, index=include_index, encoding="utf-8")


def save_figure(fig: plt.Figure, output_path: Path) -> None:
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    pdf_path = output_path.with_suffix(".pdf")
    fig.savefig(pdf_path, bbox_inches="tight")


def plot_heatmap(percent_df: pd.DataFrame, output_path: Path, title_prefix: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 4.8))

    image = ax.imshow(percent_df.values, aspect="auto", cmap=HEATMAP_CMAP)
    cbar = fig.colorbar(image, ax=ax, label="% of capability assignments")
    cbar.outline.set_linewidth(0.6)

    ax.set_xticks(range(len(percent_df.columns)))
    ax.set_xticklabels(percent_df.columns)
    ax.set_yticks(range(len(percent_df.index)))
    ax.set_yticklabels(percent_df.index)

    title = "Capabilities by ISO Family and Edge Layer"
    if title_prefix:
        title = f"{title_prefix} - {title}"

    ax.set_title(title)
    ax.set_xlabel("Edge computing layer")
    ax.set_ylabel("ISO capability family")

    max_value = percent_df.to_numpy().max() if not percent_df.empty else 0
    threshold = max_value * 0.55 if max_value else 0

    for row_idx in range(percent_df.shape[0]):
        for col_idx in range(percent_df.shape[1]):
            value = percent_df.iat[row_idx, col_idx]
            text_color = "white" if value >= threshold and value > 0 else "#23364d"
            ax.text(
                col_idx,
                row_idx,
                f"{value:.1f}",
                ha="center",
                va="center",
                fontsize=9,
                color=text_color,
                fontweight="bold" if value > 0 else "normal",
            )

    plt.tight_layout()
    save_figure(fig, output_path)
    plt.close(fig)


def plot_capability_distribution(
    table: pd.DataFrame,
    output_path: Path,
    title_prefix: str,
) -> None:
    fig, ax = plt.subplots(figsize=(7.4, 4.8))

    bar_colors = [SOFT_COLORS.get(cap, "#6c8ebf") for cap in table["iso_family"]]
    ax.barh(table["iso_family"], table["count"], color=bar_colors)

    title = "Distribution of Capabilities across ISO Families"
    if title_prefix:
        title = f"{title_prefix} - {title}"

    ax.set_title(title)
    ax.set_xlabel("Count")
    ax.set_ylabel("ISO capability family")

    for idx, value in enumerate(table["count"]):
        ax.text(value + 0.5, idx, f"{int(value)}", va="center", fontsize=9)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    save_figure(fig, output_path)
    plt.close(fig)


def plot_layer_composition(
    percent_df: pd.DataFrame,
    output_path: Path,
    title_prefix: str,
) -> None:
    """
    Stacked percentage bar chart with internal vertical layer labels.

    Important:
    This function expects a percentage table built from the PRIMARY layer dataset,
    not from the multi-layer exploded dataset.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    x = list(range(len(percent_df.index)))
    width = 0.5
    bottom = pd.Series([0.0] * len(percent_df.index), index=percent_df.index)

    for capability in CAPABILITY_ORDER:
        values = percent_df[capability]
        ax.bar(
            x,
            values,
            width=width,
            bottom=bottom.values,
            label=capability,
            color=SOFT_COLORS[capability],
            edgecolor="none",
        )
        bottom = bottom + values

    for i, layer in enumerate(percent_df.index):
        total = percent_df.iloc[i].sum()
        if total > 0:
            ax.text(
                x[i],
                3,
                layer,
                ha="center",
                va="bottom",
                rotation=90,
                fontsize=18,
                color="white",
                fontweight="bold",
            )

    title = "Capability Composition by Edge Layer"
    if title_prefix:
        title = f"{title_prefix} - {title}"

    ax.set_title(title)
    ax.set_ylabel("Percentage of capabilities")
    ax.set_xticks(x)
    ax.set_xticklabels([""] * len(percent_df.index))
    ax.set_ylim(0, 100)

    ax.legend(title="ISO Capability Family", bbox_to_anchor=(1.02, 1), loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    save_figure(fig, output_path)
    plt.close(fig)


def main() -> int:
    args = parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)

    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        df = pd.read_csv(input_path, sep=args.csv_separator, encoding=args.encoding)
    except Exception as exc:
        print(f"Error while reading CSV: {exc}", file=sys.stderr)
        return 1

    try:
        validate_columns(df, [args.repo_col, args.layer_col, *args.capability_cols])
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    tables_dir, charts_dir = ensure_directories(output_dir)

    # Multi-layer dataset: preserves cross-layer presence
    long_df_multilayer = build_long_dataset_multilayer(
        df=df,
        repo_col=args.repo_col,
        layer_col=args.layer_col,
        capability_cols=args.capability_cols,
    )

    # Primary-layer dataset: avoids double counting in stacked bars
    long_df_primary = build_long_dataset_primary_layer(
        df=df,
        repo_col=args.repo_col,
        layer_col=args.layer_col,
        capability_cols=args.capability_cols,
    )

    heatmap_counts = build_heatmap_counts(long_df_multilayer)
    heatmap_percent = build_heatmap_percent(heatmap_counts)

    capability_distribution = build_capability_distribution(long_df_primary)

    outputs = {
        "normalized_capability_dataset_multilayer": tables_dir / "normalized_capability_dataset_multilayer.csv",
        "normalized_capability_dataset_primary": tables_dir / "normalized_capability_dataset_primary.csv",
        "heatmap_capability_counts": tables_dir / "heatmap_capability_counts.csv",
        "heatmap_capability_percent": tables_dir / "heatmap_capability_percent.csv",
        "capability_distribution": tables_dir / "capability_distribution.csv",
        "fig_capability_heatmap": charts_dir / "fig_capability_heatmap.png",
        "fig_capability_distribution": charts_dir / "fig_capability_distribution.png",
        "fig_layer_capability_composition": charts_dir / "fig_layer_capability_composition.png",
    }

    save_csv(
        long_df_multilayer,
        outputs["normalized_capability_dataset_multilayer"],
        include_index=False,
    )
    save_csv(
        long_df_primary,
        outputs["normalized_capability_dataset_primary"],
        include_index=False,
    )
    save_csv(heatmap_counts, outputs["heatmap_capability_counts"], include_index=True)
    save_csv(heatmap_percent, outputs["heatmap_capability_percent"], include_index=True)
    save_csv(capability_distribution, outputs["capability_distribution"], include_index=False)

    plot_heatmap(
        heatmap_percent,
        outputs["fig_capability_heatmap"],
        args.title_prefix,
    )
    plot_capability_distribution(
        capability_distribution,
        outputs["fig_capability_distribution"],
        args.title_prefix,
    )

    summary_df = pd.DataFrame(
        [
            {
                "artifact": "normalized_capability_dataset_multilayer",
                "path": str(outputs["normalized_capability_dataset_multilayer"]),
                "rows": len(long_df_multilayer),
                "columns": len(long_df_multilayer.columns),
            },
            {
                "artifact": "normalized_capability_dataset_primary",
                "path": str(outputs["normalized_capability_dataset_primary"]),
                "rows": len(long_df_primary),
                "columns": len(long_df_primary.columns),
            },
            {
                "artifact": "heatmap_capability_counts",
                "path": str(outputs["heatmap_capability_counts"]),
                "rows": len(heatmap_counts),
                "columns": len(heatmap_counts.columns),
            },
            {
                "artifact": "heatmap_capability_percent",
                "path": str(outputs["heatmap_capability_percent"]),
                "rows": len(heatmap_percent),
                "columns": len(heatmap_percent.columns),
            },
            {
                "artifact": "capability_distribution",
                "path": str(outputs["capability_distribution"]),
                "rows": len(capability_distribution),
                "columns": len(capability_distribution.columns),
            },
            {
                "artifact": "fig_capability_heatmap",
                "path": str(outputs["fig_capability_heatmap"]),
                "rows": None,
                "columns": None,
            },
            {
                "artifact": "fig_capability_distribution",
                "path": str(outputs["fig_capability_distribution"]),
                "rows": None,
                "columns": None,
            },
        ]
    )

    summary_path = tables_dir / "analysis_summary_capability.csv"
    summary_df.to_csv(summary_path, index=False, encoding="utf-8")

    print(f"Processed capability analysis dataset: {input_path}")
    print(f"Normalized multilayer rows: {len(long_df_multilayer)}")
    print(f"Normalized primary-layer rows: {len(long_df_primary)}")
    print(f"Summary saved to: {summary_path}")
    print(f"Tables directory: {tables_dir}")
    print(f"Charts directory: {charts_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
