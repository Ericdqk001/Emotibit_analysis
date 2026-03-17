"""Correlative analysis between EmotiBit sensor means and survey scores.

Combines CS2 and MCI EmotiBit descriptive statistics, merges with survey
data, and computes Pearson correlations between 3 sensor mean values
(HR, EA, PG) and 7 survey variables. Day 1 and day 2 are analyzed separately.
"""

import sys
from pathlib import Path

import pandas as pd
from scipy import stats

SENSORS = ["HR", "EA", "PG"]
SURVEY_VARIABLES = [
    "positive_affect",
    "negative_affect",
    "VAS_nervousness",
    "VAS_interest",
    "VAS_happiness",
    "VAS_belonging",
    "VAS_wellbeing",
]
SENSOR_MEAN_COLS = [f"{s}_mean" for s in SENSORS]

ID_CORRECTIONS = {
    "MCI-01": "INTACT-MCI-01",
    "MCI-04": "INTACT-MCI-04",
    "INACT-CS2-Y-13": "INTACT-CS2-Y-13",
}


def load_emotibit_combined(cs2_path: Path, mci_path: Path) -> pd.DataFrame:
    """Load and combine CS2 and MCI emotibit stats into wide format.

    Returns DataFrame with columns:
        day, participant, HR_mean, EA_mean, PG_mean
    """
    cs2 = pd.read_csv(cs2_path)
    mci = pd.read_csv(mci_path)

    cols = ["day", "participant", "sensor", "mean"]
    combined = pd.concat([cs2[cols], mci[cols]], ignore_index=True)

    wide = combined.pivot_table(
        index=["day", "participant"],
        columns="sensor",
        values="mean",
    ).reset_index()

    wide.columns = [f"{col}_mean" if col in SENSORS else col for col in wide.columns]

    return wide


def load_survey_data(survey_path: Path) -> pd.DataFrame:
    """Load survey scores for both days with corrected participant IDs.

    Returns DataFrame with columns:
        day, participant, positive_affect, negative_affect,
        VAS_nervousness, VAS_interest, VAS_happiness,
        VAS_belonging, VAS_wellbeing
    """
    all_days = []
    for day in ["day1", "day2"]:
        df = pd.read_excel(survey_path, sheet_name=f"{day}_scores")
        df["day"] = day
        df["ParticipantID"] = df["ParticipantID"].replace(ID_CORRECTIONS)
        all_days.append(df)

    result = pd.concat(all_days, ignore_index=True)
    result = result.rename(columns={"ParticipantID": "participant"})
    return result


def merge_data(emotibit: pd.DataFrame, survey: pd.DataFrame) -> pd.DataFrame:
    """Merge emotibit sensor means with survey scores on (day, participant)."""
    merged = emotibit.merge(survey, on=["day", "participant"], how="inner")
    print(
        f"Merged: {len(merged)} rows (emotibit: {len(emotibit)}, survey: {len(survey)})"
    )
    return merged


def compute_correlations(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute Pearson correlations between sensor means and survey variables.

    Returns:
        Tuple of (r_matrix, p_matrix), both 3x7 DataFrames.
    """
    r_values = {}
    p_values = {}

    for sensor_col in SENSOR_MEAN_COLS:
        r_row = {}
        p_row = {}
        for survey_var in SURVEY_VARIABLES:
            valid = df[[sensor_col, survey_var]].dropna()
            if len(valid) < 3:
                r_row[survey_var] = float("nan")
                p_row[survey_var] = float("nan")
            else:
                corr = stats.pearsonr(valid[sensor_col], valid[survey_var])
                r_row[survey_var] = round(float(corr[0]), 4)  # type: ignore[arg-type]
                p_row[survey_var] = round(float(corr[1]), 4)  # type: ignore[arg-type]
        r_values[sensor_col] = r_row
        p_values[sensor_col] = p_row

    r_matrix = pd.DataFrame(r_values).T
    p_matrix = pd.DataFrame(p_values).T

    return r_matrix, p_matrix


def save_results(
    r_matrix: pd.DataFrame,
    p_matrix: pd.DataFrame,
    day: str,
    output_dir: Path,
) -> None:
    """Save correlation results to CSV files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    r_path = output_dir / f"correlation_{day}_r_values.csv"
    r_matrix.to_csv(r_path, index_label="sensor")
    print(f"Saved r-values: {r_path}")

    p_path = output_dir / f"correlation_{day}_p_values.csv"
    p_matrix.to_csv(p_path, index_label="sensor")
    print(f"Saved p-values: {p_path}")


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent.parent

    cs2_path = (
        project_root / "src" / "CS2" / "output" / "emotibit_CS2_descriptive_stats.csv"
    )
    mci_path = project_root / "src" / "MCI" / "output" / "mci_descriptive_stats.csv"
    survey_path = script_dir.parent / "outputs" / "survey_results.xlsx"
    output_dir = script_dir.parent / "outputs"

    for path, name in [
        (cs2_path, "CS2 stats"),
        (mci_path, "MCI stats"),
        (survey_path, "Survey data"),
    ]:
        if not path.exists():
            print(f"Error: {name} not found at {path}")
            sys.exit(1)

    # Step 1: Load data
    print("=" * 60)
    print("STEP 1: Loading data")
    print("=" * 60)
    emotibit = load_emotibit_combined(cs2_path, mci_path)
    print(f"EmotiBit combined: {len(emotibit)} rows")

    survey = load_survey_data(survey_path)
    print(f"Survey data: {len(survey)} rows")

    # Check which survey participants are missing from emotibit data
    survey_keys = set(zip(survey["day"], survey["participant"], strict=True))
    emotibit_keys = set(zip(emotibit["day"], emotibit["participant"], strict=True))
    missing = sorted(survey_keys - emotibit_keys)
    if missing:
        print(f"\nMissing from emotibit data ({len(missing)}):")
        for day, pid in missing:
            print(f"  {day}/{pid}")

    # Step 2: Merge
    print("\n" + "=" * 60)
    print("STEP 2: Merging emotibit and survey data")
    print("=" * 60)
    merged = merge_data(emotibit, survey)

    if merged.empty:
        print("No matching data found. Check participant IDs.")
        sys.exit(1)

    # Save merged data
    merged.to_csv(output_dir / "correlation_merged_data.csv", index=False)
    print(f"Saved merged data: {output_dir / 'correlation_merged_data.csv'}")

    # Step 3: Compute correlations separately for each day
    print("\n" + "=" * 60)
    print("STEP 3: Pearson correlations")
    print("=" * 60)

    for day in ["day1", "day2"]:
        day_data = merged[merged["day"] == day]
        print(f"\n--- {day} ({len(day_data)} observations) ---")

        if len(day_data) < 3:
            print(f"  Insufficient data for {day}, skipping")
            continue

        day_df: pd.DataFrame = day_data  # type: ignore[assignment]
        r_matrix, p_matrix = compute_correlations(day_df)

        print("\nCorrelation coefficients (r):")
        print(r_matrix.to_string())
        print("\nP-values:")
        print(p_matrix.to_string())

        save_results(r_matrix, p_matrix, day, output_dir)
