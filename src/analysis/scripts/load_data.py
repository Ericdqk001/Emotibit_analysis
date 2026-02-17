"""Load parsed EmotiBit sensor data.

Adapted from code_examples/loading_data.py pattern:
1. Extract timestamp from filename
2. Load CSV with LocalTimestamp column
3. Convert to AbsoluteTime (UTC) and relative Time_s
"""

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

# Sensors to load by default (matching example/ pattern for TABLE 1)
DEFAULT_SENSORS = ["HR", "EA", "PG"]  # Heart Rate, EDA, PPG Green


@dataclass
class RecordingInfo:
    """Metadata for one recording (one participant, one day)."""

    pair_id: str
    participant: str
    day: str
    path: Path
    timestamp: str


def load_metadata(metadata_path: Path) -> dict:
    """Load project metadata from JSON."""
    with open(metadata_path) as f:
        return json.load(f)


def discover_recordings(base_path: Path) -> list[RecordingInfo]:
    """Find all recordings in restructured emotibit folder.

    Structure: base_path/day{1,2}/Pair{1-6}/{O,Y}-XX/
    """
    recordings = []

    for day_dir in sorted(base_path.glob("day*")):
        for pair_dir in sorted(day_dir.glob("Pair*")):
            for participant_dir in sorted(pair_dir.glob("*-*")):
                # Find parsed sensor files to get timestamp
                sensor_files = list(participant_dir.glob("*_EA.csv"))
                if sensor_files:
                    # Extract timestamp from filename: {timestamp}_EA.csv
                    timestamp = sensor_files[0].stem.rsplit("_", 1)[0]
                    recordings.append(
                        RecordingInfo(
                            pair_id=pair_dir.name,
                            participant=participant_dir.name,
                            day=day_dir.name,
                            path=participant_dir,
                            timestamp=timestamp,
                        )
                    )

    return recordings


def load_sensor(csv_path: Path) -> pd.DataFrame:
    """Load a single parsed sensor CSV.

    Pattern from code_examples/loading_data.py:
    - LocalTimestamp column → AbsoluteTime (UTC datetime)
    - Create relative Time_s from first timestamp
    """
    df = pd.read_csv(csv_path)

    if "LocalTimestamp" in df.columns:
        df["LocalTimestamp"] = pd.to_numeric(df["LocalTimestamp"], errors="coerce")
        df = df.dropna(subset=["LocalTimestamp"])

        # Convert to UTC datetime (line 47-49 from example)
        df["AbsoluteTime"] = pd.to_datetime(df["LocalTimestamp"], unit="s", utc=True)

        # Relative time in seconds (line 52-53 from example)
        first_ts = df["LocalTimestamp"].iloc[0]
        df["Time_s"] = df["LocalTimestamp"] - first_ts

    return df


def load_recording(
    recording_path: Path,
    timestamp: str,
    sensors: list[str] | None = None,
) -> dict[str, pd.DataFrame]:
    """Load all sensor files for one recording.

    Args:
        recording_path: Directory containing parsed sensor CSVs
        timestamp: Recording timestamp (e.g., "2025-10-13_14-49-24-526653")
        sensors: List of sensors to load (default: DEFAULT_SENSORS)

    Returns:
        Dict mapping sensor name to DataFrame
    """
    if sensors is None:
        sensors = DEFAULT_SENSORS

    data = {}
    for sensor in sensors:
        csv_path = recording_path / f"{timestamp}_{sensor}.csv"
        if csv_path.exists():
            df = load_sensor(csv_path)
            if not df.empty:
                data[sensor] = df

    return data


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        base_path = Path(sys.argv[1])
        recordings = discover_recordings(base_path)
        print(f"Found {len(recordings)} recordings:\n")
        for r in recordings:
            print(f"  {r.day}/{r.pair_id}/{r.participant}")

        # Load first recording as test
        if recordings:
            print(f"\nLoading first recording: {recordings[0].path}")
            data = load_recording(recordings[0].path, recordings[0].timestamp)
            print(f"Loaded {len(data)} sensors:")
            for sensor, df in data.items():
                print(
                    f"  {sensor}: {len(df)} samples, {df['Time_s'].max():.1f}s duration"
                )
    else:
        print("Usage: python load_data.py <emotibit_base_path>")
        print("\nExample:")
        print("  python load_data.py /Volumes/INT-ACT/INTACT-CS2_restructured/emotibit")
