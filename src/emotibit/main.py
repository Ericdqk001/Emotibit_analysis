"""EmotiBit analysis pipeline.

Parses, loads, and computes descriptive statistics for all EmotiBit recordings.

Usage:
    python src/emotibit/main.py <dataparser_path> <emotibit_data_path>

Example:
    python src/emotibit/main.py /path/to/EmotiBitDataParser /path/to/emotibit
"""

import sys
from pathlib import Path

# Add scripts dir to path for imports
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from src.emotibit.scripts.describe import compute_recording_stats
from src.emotibit.scripts.load import discover_recordings, load_recording
from src.emotibit.scripts.parse import parse_all_recordings


def main(parser_path: Path, data_path: Path) -> None:
    import pandas as pd

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    # Step 1: Parse all recordings
    # Comment out if already parsed
    print("=" * 60)
    print("STEP 1: Parsing raw EmotiBit data")
    print("=" * 60)
    counts = parse_all_recordings(data_path, parser_path)
    print(f"\nParsing summary: {counts['parsed']} parsed, {counts['failed']} failed")

    # Step 2: Load and compute stats for all recordings
    print("\n" + "=" * 60)
    print("STEP 2: Loading and computing descriptive statistics")
    print("=" * 60)
    recordings = discover_recordings(data_path)
    print(f"Found {len(recordings)} recordings\n")

    all_stats = []
    for r in recordings:
        print(f"  Processing: {r.day}/{r.pair_id}/{r.participant}")
        data = load_recording(r.path, r.timestamp)
        if not data:
            print("    No sensor data loaded, skipping")
            continue

        stats_df = compute_recording_stats(data)
        stats_df["day"] = r.day
        stats_df["pair"] = r.pair_id
        stats_df["participant"] = r.participant
        all_stats.append(stats_df)

    if not all_stats:
        print("No recordings loaded successfully")
        return

    # Step 3: Save results
    print("\n" + "=" * 60)
    print("STEP 3: Saving results")
    print("=" * 60)
    result = pd.concat(all_stats, ignore_index=True)

    # Reorder columns so identifiers come first
    id_cols = ["day", "pair", "participant", "sensor"]
    other_cols = [c for c in result.columns if c not in id_cols]
    result = result[id_cols + other_cols]

    output_file = output_dir / "emotibit_descriptive_stats.csv"
    result.to_csv(output_file, index=False)
    print(f"Saved to: {output_file}")
    print(f"\n{result.to_string(index=False)}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: python src/emotibit/main.py <dataparser_path> <emotibit_data_path>"
        )
        print("\nExample:")
        print(
            " python src/emotibit/main.py /path/to/EmotiBitDataParser /path/to/emotibit"
        )
        sys.exit(1)

    parser_path = Path(sys.argv[1])
    data_path = Path(sys.argv[2])

    if not parser_path.exists():
        print(f"Error: DataParser not found at {parser_path}")
        sys.exit(1)

    if not data_path.exists():
        print(f"Error: Data path not found at {data_path}")
        sys.exit(1)

    main(parser_path, data_path)
