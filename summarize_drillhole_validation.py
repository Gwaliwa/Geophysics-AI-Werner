#!/usr/bin/env python3
"""
Summarize drillhole validation results for the Werner-enhanced prospectivity model.

This script supports two input styles:

1. Already summarized table:
   columns such as Dataset, Count, Mean_Prospectivity, Top20_%, Within_1km_%,
   Within_5km_%, Within_10km_%

2. Point-level drillhole table:
   required:
       prospectivity
   optional:
       geochem / Geochem / geochem_flag
       distance_to_top20_km / distance_km / distance_to_high_prospectivity_km
       top20 / in_top20 / top20_zone

Example:
    python scripts/summarize_drillhole_validation.py \
        --input data/drillhole_prospectivity_validation.csv \
        --output outputs/drillhole_validation_summary.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


GEOCHEM_COLUMNS = ["geochem", "Geochem", "geochem_flag", "Geochem_Flag", "GEOCHEM"]
DISTANCE_COLUMNS = [
    "distance_to_top20_km",
    "distance_km",
    "distance_to_high_prospectivity_km",
    "nearest_top20_distance_km",
]
TOP20_COLUMNS = ["top20", "in_top20", "top20_zone", "Top20"]


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Return the first matching column name from a list of candidates."""
    for col in candidates:
        if col in df.columns:
            return col
    return None


def looks_summarized(df: pd.DataFrame) -> bool:
    """Check whether the table is already a summary table."""
    required = {"Dataset", "Count"}
    return required.issubset(set(df.columns))


def normalize_geochem(value) -> str:
    """Normalize geochemical classification labels."""
    text = str(value).strip().lower()
    if text in {"y", "yes", "true", "1", "anomalous", "geochem = y"}:
        return "Geochem = Y"
    if text in {"n", "no", "false", "0", "non-anomalous", "non_anomalous", "geochem = n"}:
        return "Geochem = N"
    return str(value)


def summarize_point_level(df: pd.DataFrame) -> pd.DataFrame:
    """Generate validation summary from point-level drillhole data."""
    prospectivity_col = None
    for col in ["prospectivity", "Mean_Prospectivity", "predicted_prospectivity", "score"]:
        if col in df.columns:
            prospectivity_col = col
            break

    if prospectivity_col is None:
        raise ValueError(
            "Point-level input must include a prospectivity column, such as "
            "'prospectivity' or 'predicted_prospectivity'."
        )

    geochem_col = find_column(df, GEOCHEM_COLUMNS)
    distance_col = find_column(df, DISTANCE_COLUMNS)
    top20_col = find_column(df, TOP20_COLUMNS)

    df = df.copy()
    df[prospectivity_col] = pd.to_numeric(df[prospectivity_col], errors="coerce")

    if geochem_col is not None:
        df["_dataset_group"] = df[geochem_col].apply(normalize_geochem)
    else:
        df["_dataset_group"] = "All Drillholes"

    groups = [("All Drillholes", df)]
    for group_name, group_df in df.groupby("_dataset_group"):
        if group_name != "All Drillholes":
            groups.append((group_name, group_df))

    rows = []
    for name, group in groups:
        row = {
            "Dataset": name,
            "Count": int(len(group)),
            "Mean_Prospectivity": round(group[prospectivity_col].mean(), 3),
        }

        if top20_col is not None:
            top20_numeric = group[top20_col].astype(str).str.lower().isin(["1", "true", "yes", "y"])
            row["Top20_%"] = round(top20_numeric.mean() * 100, 2)

        if distance_col is not None:
            dist = pd.to_numeric(group[distance_col], errors="coerce")
            row["Median_Distance_km"] = round(dist.median(), 3)
            row["Within_1km_%"] = round((dist <= 1).mean() * 100, 2)
            row["Within_5km_%"] = round((dist <= 5).mean() * 100, 2)
            row["Within_10km_%"] = round((dist <= 10).mean() * 100, 2)

        rows.append(row)

    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize drillhole validation results.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/drillhole_prospectivity_validation.csv"),
        help="Input drillhole validation CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/drillhole_validation_summary.csv"),
        help="Output summary CSV.",
    )
    args = parser.parse_args()

    df = pd.read_csv(args.input)

    if looks_summarized(df):
        summary = df.copy()
    else:
        summary = summarize_point_level(df)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.output, index=False)

    print(summary.to_string(index=False))
    print(f"\nSaved drillhole validation summary to: {args.output}")


if __name__ == "__main__":
    main()
