"""MCI EmotiBit analysis pipeline.

Loads and computes descriptive statistics for all MCI EmotiBit recordings.

Usage:
    python src/MCI/main.py <data_path>

Example:
    python src/MCI/main.py data/INTACT-MCI_restructured
"""

import sys
from pathlib import Path

import pandas as pd
from scripts.describe import compute_recording_stats
from scripts.load import discover_recordings, load_recording


def main(data_path: Path) -> None:
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    emotibit_path = data_path / "emotibit"

    # Step 1: Load and compute stats for all recordings
    print("=" * 60)
    print("STEP 1: Loading and computing descriptive statistics")
    print("=" * 60)
    recordings = discover_recordings(emotibit_path)
    print(f"Found {len(recordings)} recordings\n")

    all_stats = []
    for r in recordings:
        print(f"  Processing: {r.day}/{r.participant}")
        try:
            data = load_recording(r.path, r.timestamp)
            if not data:
                print("    No sensor data loaded, skipping")
                continue

            stats_df = compute_recording_stats(data)
            stats_df["day"] = r.day
            stats_df["participant"] = r.participant
            all_stats.append(stats_df)
        except Exception as e:
            print(
                f"    ERROR processing {r.day}/{r.participant}: {type(e).__name__}: {e}"
            )
            print(f"    Recording path: {r.path}")
            print(f"    Timestamp: {r.timestamp}")
            continue

    if not all_stats:
        print("No recordings loaded successfully")
        return

    # Step 2: Save results
    print("\n" + "=" * 60)
    print("STEP 2: Saving results")
    print("=" * 60)
    result = pd.concat(all_stats, ignore_index=True)

    # Reorder columns so identifiers come first
    id_cols = ["day", "participant", "sensor"]
    other_cols = [c for c in result.columns if c not in id_cols]
    result = result[id_cols + other_cols]

    output_file = output_dir / "mci_descriptive_stats.csv"
    result.to_csv(output_file, index=False)
    print(f"Saved to: {output_file}")
    print(f"\n{result.to_string(index=False)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python src/MCI/main.py <data_path>")
        print("\nExample:")
        print("  python src/MCI/main.py data/INTACT-MCI_restructured")
        sys.exit(1)

    data_path = Path(sys.argv[1])

    if not data_path.exists():
        print(f"Error: Data path not found at {data_path}")
        sys.exit(1)

    main(data_path)
