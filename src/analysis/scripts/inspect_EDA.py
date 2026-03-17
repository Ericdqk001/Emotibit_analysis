"""Inspect EDA (EA) data across all participants.

Loads CS2 and MCI descriptive stats, filters EA sensor data,
flags saturated recordings (max == 10000), and saves to Excel.
"""

from pathlib import Path

import pandas as pd


def load_eda_stats(cs2_path: Path, mci_path: Path) -> pd.DataFrame:
    """Load CS2 and MCI stats, filter to EA sensor only."""
    cs2 = pd.read_csv(cs2_path)
    mci = pd.read_csv(mci_path)

    combined = pd.concat([cs2, mci], ignore_index=True)
    ea = combined[combined["sensor"] == "EA"].copy()

    # Flag saturated recordings
    ea["saturated"] = ea["max"] == 10000.0

    # Drop sensor column (all EA)
    ea = ea.drop(columns=["sensor"])

    return ea  # type: ignore[return-value]


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent.parent

    cs2_path = (
        project_root / "src" / "CS2" / "output" / "emotibit_CS2_descriptive_stats.csv"
    )
    mci_path = project_root / "src" / "MCI" / "output" / "mci_descriptive_stats.csv"
    output_dir = script_dir.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    ea = load_eda_stats(cs2_path, mci_path)

    print(f"Total EA recordings: {len(ea)}")
    print(f"Saturated (max=10000): {ea['saturated'].sum()}")
    print(f"\n{ea.to_string(index=False)}")

    output_path = output_dir / "eda_inspection.xlsx"
    ea.to_excel(output_path, index=False)
    print(f"\nSaved to: {output_path}")
