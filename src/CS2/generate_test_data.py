"""Generate fake parsed EmotiBit data for testing the load and describe pipeline."""

from pathlib import Path

import numpy as np
import pandas as pd


def generate_sensor_data(
    sensor: str, n_samples: int, duration_s: float, start_ts: float
) -> pd.DataFrame:
    """Generate fake sensor data with realistic values."""
    timestamps = np.linspace(start_ts, start_ts + duration_s, n_samples)

    if sensor == "HR":
        values = np.random.normal(loc=75, scale=8, size=n_samples)
    elif sensor == "EA":
        values = np.random.exponential(scale=0.02, size=n_samples)
    elif sensor == "PG":
        values = np.random.normal(loc=450, scale=120, size=n_samples)
    else:
        values = np.random.randn(n_samples)

    return pd.DataFrame({"LocalTimestamp": timestamps, sensor: values})


def main():
    base = Path(__file__).parent / "test_data"

    participants = {
        "day1": {"Pair1": ["O-01", "Y-02"], "Pair2": ["O-03", "Y-04"]},
        "day2": {"Pair1": ["O-01", "Y-02"], "Pair2": ["O-03", "Y-04"]},
    }

    sensors = {
        "HR": {"n_samples": 1076, "duration_s": 860},
        "EA": {"n_samples": 12900, "duration_s": 860},
        "PG": {"n_samples": 21500, "duration_s": 860},
    }

    start_ts = 1697200000.0  # arbitrary Unix timestamp
    timestamp_str = "2025-01-01_10-00-00-000000"

    for day, pairs in participants.items():
        for pair, pids in pairs.items():
            for pid in pids:
                folder = base / day / pair / pid
                folder.mkdir(parents=True, exist_ok=True)

                for sensor, params in sensors.items():
                    df = generate_sensor_data(
                        sensor, params["n_samples"], params["duration_s"], start_ts
                    )
                    df.to_csv(folder / f"{timestamp_str}_{sensor}.csv", index=False)

                print(f"  Created: {day}/{pair}/{pid}")

    print(f"\nTest data saved to: {base}")


if __name__ == "__main__":
    main()
