"""Compute descriptive statistics for EmotiBit sensor data.

Pattern from code_examples/emotibit_task_analysis.py:
- mean, std (ddof=1), min, max, median, mode, n_samples
Plus: duration, sampling_rate, percentiles
"""

from pathlib import Path

import pandas as pd


def compute_sensor_stats(df: pd.DataFrame, value_col: str) -> dict:
    """Compute descriptive statistics for one sensor.

    Args:
        df: DataFrame with sensor data (must have Time_s and value_col)
        value_col: Name of the sensor value column (e.g., "EA", "HR")

    Returns:
        Dictionary of statistics
    """
    # Convert to numeric, handling mixed int/str types from chunked CSV reading
    values: pd.Series = pd.to_numeric(df[value_col], errors="coerce").dropna()  # type: ignore[assignment]

    if len(values) == 0:
        return {"n_samples": 0}

    # Duration and sampling rate
    duration_s = df["Time_s"].max() - df["Time_s"].min()
    sampling_rate = len(values) / duration_s if duration_s > 0 else 0

    # Basic stats (matching code_examples/emotibit_task_analysis.py lines 114-123)
    result = {
        "n_samples": len(values),
        "duration_s": round(duration_s, 2),
        "sampling_rate_hz": round(sampling_rate, 2),
        "mean": round(values.mean(), 4),
        "std": round(values.std(ddof=1), 4),  # Bessel's correction
        "min": round(values.min(), 4),
        "max": round(values.max(), 4),
        "median": round(values.median(), 4),
        "q25": round(values.quantile(0.25), 4),
        "q75": round(values.quantile(0.75), 4),
    }

    return result


def compute_recording_stats(
    data: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Compute stats for all sensors in a recording.

    Args:
        data: Dict mapping sensor name to DataFrame

    Returns:
        DataFrame with one row per sensor
    """
    rows = []
    for sensor, df in data.items():
        try:
            sensor_stats = compute_sensor_stats(df, sensor)
            sensor_stats["sensor"] = sensor
            rows.append(sensor_stats)
        except Exception as e:
            print(f"      ERROR in sensor '{sensor}': {type(e).__name__}: {e}")
            # Print sample of problematic values
            values = df[sensor]
            print(f"      Data type: {values.dtype}")
            print(f"      Total values: {len(values)}")

            # Check all unique types (not just first 100)
            all_types = {type(v).__name__ for v in values.dropna()}
            print(f"      All unique types in data: {all_types}")

            # Find and print string values
            string_values = [v for v in values if isinstance(v, str)]
            if string_values:
                print(f"      Found {len(string_values)} string values")
                print(f"      First 10 strings: {string_values[:10]}")
                # Find indices of string values
                string_indices = [i for i, v in enumerate(values) if isinstance(v, str)]
                print(
                    f"      String locations (first 10 indices): {string_indices[:10]}"
                )
            raise

    result = pd.DataFrame(rows)

    # Reorder columns
    cols = [
        "sensor",
        "n_samples",
        "duration_s",
        "sampling_rate_hz",
        "mean",
        "std",
        "min",
        "q25",
        "median",
        "q75",
        "max",
    ]
    selected_cols = [c for c in cols if c in result.columns]
    if not selected_cols:
        return pd.DataFrame()
    df_result = result[selected_cols]
    return df_result if isinstance(df_result, pd.DataFrame) else df_result.to_frame().T


def print_stats_table(stats_df: pd.DataFrame) -> None:
    """Print statistics as a formatted table."""
    print("\n" + "=" * 80)
    print("DESCRIPTIVE STATISTICS")
    print("=" * 80)
    print(stats_df.to_string(index=False))
    print("=" * 80)


def save_stats(stats_df: pd.DataFrame, output_path: Path) -> None:
    """Save statistics to CSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    stats_df.to_csv(output_path, index=False)
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    pass
