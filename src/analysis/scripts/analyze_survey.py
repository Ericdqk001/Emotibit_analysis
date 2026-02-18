"""Analyze survey data from the INT-ACT study.

Loads survey CSVs and computes:
- PANAS positive and negative affect scores (2 variables)
- VAS scores for nervousness, interest, happiness, belonging, wellbeing (5 variables)
- Descriptive statistics for all 7 variables
"""

from pathlib import Path

import pandas as pd

POSITIVE_ITEMS = [
    "panas01",
    "panas03",
    "panas05",
    "panas09",
    "panas10",
    "panas12",
    "panas14",
    "panas16",
    "panas17",
    "panas19",
]

NEGATIVE_ITEMS = [
    "panas02",
    "panas04",
    "panas06",
    "panas07",
    "panas08",
    "panas11",
    "panas13",
    "panas15",
    "panas18",
    "panas20",
]

VAS_COLUMNS = {
    "VAS_nervousness": "vas1nervousness[SQ001]",
    "VAS_interest": "vas2interest[SQ001]",
    "VAS_happiness": "vas3happiness[SQ001]",
    "VAS_belonging": "vas4belonging[SQ001]",
    "VAS_wellbeing": "vas5wellbeing[SQ001]",
}


def load_survey(csv_path: Path) -> pd.DataFrame:
    """Load a survey CSV (semicolon-delimited)."""
    return pd.read_csv(csv_path, sep=";")


def compute_panas_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Compute PANAS positive and negative affect scores.

    Positive Affect: sum of items 1, 3, 5, 9, 10, 12, 14, 16, 17, 19
    Negative Affect: sum of items 2, 4, 6, 7, 8, 11, 13, 15, 18, 20

    Each score ranges from 10 to 50.
    """
    pos_cols = [f"panas[{item}]" for item in POSITIVE_ITEMS]
    neg_cols = [f"panas[{item}]" for item in NEGATIVE_ITEMS]

    result = pd.DataFrame()
    result["ParticipantID"] = df["ParticipantID"]
    result["positive_affect"] = df[pos_cols].sum(axis=1)
    result["negative_affect"] = df[neg_cols].sum(axis=1)

    return result


def extract_vas_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Extract 5 VAS scores (each 1-100).

    Nervousness (1=calm, 100=nervous)
    Interest (1=bored, 100=interested)
    Happiness (1=sad, 100=happy)
    Belonging (1=isolated, 100=connected)
    Wellbeing (1=absent, 100=maximum wellness)
    """
    result = pd.DataFrame()
    result["ParticipantID"] = df["ParticipantID"]

    for name, col in VAS_COLUMNS.items():
        result[name] = pd.to_numeric(df[col], errors="coerce")

    return result


def extract_all_survey_variables(df: pd.DataFrame) -> pd.DataFrame:
    """Extract all 7 survey variables for a given day.

    Returns DataFrame with columns:
        ParticipantID, positive_affect, negative_affect,
        nervousness, interest, happiness, belonging, wellbeing
    """
    panas = compute_panas_scores(df)
    vas = extract_vas_scores(df)

    return panas.merge(vas, on="ParticipantID")


def compute_descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Compute descriptive statistics for all 7 survey variables.

    Returns a DataFrame with one row per variable and columns:
        n, mean, std, min, q25, median, q75, max
    """
    variables = [
        "positive_affect",
        "negative_affect",
        "VAS_nervousness",
        "VAS_interest",
        "VAS_happiness",
        "VAS_belonging",
        "VAS_wellbeing",
    ]

    rows = []
    for var in variables:
        values = df[var].dropna()
        rows.append(
            {
                "variable": var,
                "n": len(values),
                "mean": round(values.mean(), 2),
                "std": round(values.std(ddof=1), 2),
                "min": round(values.min(), 2),
                "q25": round(values.quantile(0.25), 2),
                "median": round(values.median(), 2),
                "q75": round(values.quantile(0.75), 2),
                "max": round(values.max(), 2),
            }
        )

    return pd.DataFrame(rows)


if __name__ == "__main__":
    data_dir = Path(__file__).resolve().parent.parent.parent.parent / "data" / "surveys"
    output_dir = Path(__file__).resolve().parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(output_dir / "survey_results.xlsx") as writer:
        for day in ["day1", "day2"]:
            csv_path = data_dir / f"{day}.csv"
            if not csv_path.exists():
                print(f"Not found: {csv_path}")
                continue

            df = load_survey(csv_path)
            if df.empty:
                print(f"{day}: no data rows")
                continue

            all_vars = extract_all_survey_variables(df)
            all_vars.to_excel(writer, sheet_name=f"{day}_scores", index=False)

            stats = compute_descriptive_stats(all_vars)
            stats.to_excel(writer, sheet_name=f"{day}_stats", index=False)

            print(f"\n{day} - all 7 survey variables:")
            print(all_vars.to_string(index=False))
            print(f"\n{day} - descriptive statistics:")
            print(stats.to_string(index=False))

    print(f"\nSaved to: {output_dir / 'survey_results.xlsx'}")
