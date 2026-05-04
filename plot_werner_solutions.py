#!/usr/bin/env python3
"""
Plot Werner deconvolution solution outputs.

Expected input:
    data/werner_solutions.csv

Required columns:
    peak_col, peak_row, z0_depth

Optional columns:
    quality_score, orientation, method

Example:
    python scripts/plot_werner_solutions.py \
        --input data/werner_solutions.csv \
        --output figures/werner_solutions_depth.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


REQUIRED_COLUMNS = ["peak_col", "peak_row", "z0_depth"]


def load_werner_solutions(path: Path) -> pd.DataFrame:
    """Load and validate Werner solution table."""
    df = pd.read_csv(path)

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    for col in REQUIRED_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if "quality_score" in df.columns:
        df["quality_score"] = pd.to_numeric(df["quality_score"], errors="coerce")

    df = df.dropna(subset=REQUIRED_COLUMNS)
    return df


def plot_spatial_depth(df: pd.DataFrame, output: Path) -> None:
    """Create spatial scatter plot of Werner solutions colored by depth."""
    output.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(9, 7))

    if "quality_score" in df.columns:
        sizes = 30 + 30 * (df["quality_score"].fillna(0) / max(df["quality_score"].max(), 1))
    else:
        sizes = 40

    scatter = plt.scatter(
        df["peak_col"],
        df["peak_row"],
        c=df["z0_depth"],
        s=sizes,
        alpha=0.8,
        edgecolors="black",
        linewidths=0.3,
    )

    plt.gca().invert_yaxis()
    plt.xlabel("Raster column / profile x-position")
    plt.ylabel("Raster row / profile y-position")
    plt.title("Werner deconvolution source solutions by estimated depth")
    cbar = plt.colorbar(scatter)
    cbar.set_label("Estimated depth, z0")
    plt.tight_layout()
    plt.savefig(output, dpi=300)
    plt.close()


def plot_depth_histogram(df: pd.DataFrame, output: Path) -> None:
    """Create histogram of Werner estimated source depths."""
    output.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 5))
    plt.hist(df["z0_depth"], bins=15)
    plt.xlabel("Estimated depth, z0")
    plt.ylabel("Number of Werner solutions")
    plt.title("Distribution of Werner estimated source depths")
    plt.tight_layout()
    plt.savefig(output, dpi=300)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot Werner deconvolution solution outputs.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/werner_solutions.csv"),
        help="Input Werner solution CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("figures/werner_solutions_depth.png"),
        help="Output spatial-depth figure path.",
    )
    parser.add_argument(
        "--histogram-output",
        type=Path,
        default=Path("figures/werner_depth_histogram.png"),
        help="Output depth histogram path.",
    )
    args = parser.parse_args()

    df = load_werner_solutions(args.input)
    plot_spatial_depth(df, args.output)
    plot_depth_histogram(df, args.histogram_output)

    print(f"Saved Werner solutions spatial-depth figure to: {args.output}")
    print(f"Saved Werner depth histogram to: {args.histogram_output}")


if __name__ == "__main__":
    main()
