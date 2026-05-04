#!/usr/bin/env python3
"""
Plot feature importance results for the Werner-enhanced prospectivity model.

Expected input:
    data/feature_importance_werner_enhanced_no_leakage.csv

The CSV should contain either:
    - columns named: feature, importance
or
    - two unnamed columns where column 1 = feature and column 2 = importance

Example:
    python scripts/plot_feature_importance.py \
        --input data/feature_importance_werner_enhanced_no_leakage.csv \
        --output figures/feature_importance_werner_enhanced.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def load_feature_importance(path: Path) -> pd.DataFrame:
    """Load and standardize feature-importance table."""
    df = pd.read_csv(path)

    # Handle unnamed two-column CSVs.
    if "feature" not in df.columns or "importance" not in df.columns:
        if df.shape[1] < 2:
            raise ValueError("Input CSV must contain at least two columns: feature and importance.")
        df = df.iloc[:, :2].copy()
        df.columns = ["feature", "importance"]

    df["feature"] = df["feature"].astype(str)
    df["importance"] = pd.to_numeric(df["importance"], errors="coerce")
    df = df.dropna(subset=["importance"])
    df = df.sort_values("importance", ascending=True)

    return df


def plot_feature_importance(df: pd.DataFrame, output: Path, top_n: int | None = None) -> None:
    """Create a horizontal bar chart of feature importance."""
    if top_n is not None and top_n > 0:
        df = df.tail(top_n)

    output.parent.mkdir(parents=True, exist_ok=True)

    height = max(6, 0.35 * len(df))
    plt.figure(figsize=(10, height))
    plt.barh(df["feature"], df["importance"])
    plt.xlabel("Feature importance")
    plt.ylabel("Predictor")
    plt.title("Werner-enhanced model feature importance")
    plt.tight_layout()
    plt.savefig(output, dpi=300)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot Werner-enhanced model feature importance.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/feature_importance_werner_enhanced_no_leakage.csv"),
        help="Path to feature-importance CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("figures/feature_importance_werner_enhanced.png"),
        help="Output figure path.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=25,
        help="Number of top predictors to plot. Use 0 to plot all.",
    )
    args = parser.parse_args()

    df = load_feature_importance(args.input)
    top_n = None if args.top_n == 0 else args.top_n
    plot_feature_importance(df, args.output, top_n=top_n)

    print(f"Saved feature-importance figure to: {args.output}")


if __name__ == "__main__":
    main()
