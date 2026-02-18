"""MCI EmotiBit analysis pipeline.

Restructures, parses, loads, and computes descriptive statistics
for all MCI EmotiBit recordings.

Usage:
    python src/MCI/main.py <dataparser_path> <source_path> <output_path>

Example (macOS):
    python src/MCI/main.py <parser_path> <source_path> <output_path>
    parser_path: .../EmotiBitDataParser.app/Contents/MacOS/EmotiBitDataParser
    source_path: /Volumes/INT-ACT/INTACT-MCI/emotibit
    output_path: /Volumes/INT-ACT/INTACT-MCI_restructured
"""

import sys
from pathlib import Path

import pandas as pd
from scripts.describe import compute_recording_stats
from scripts.load import discover_recordings, load_recording
from scripts.parse import parse_all_recordings
from scripts.restructure_folder import restructure_mci


def main(parser_path: Path, source_path: Path, output_path: Path) -> None:
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    emotibit_path = output_path / "emotibit"

    # Step 1: Restructure flat folder into structured directories
    print("=" * 60)
    print("STEP 1: Restructuring MCI data")
    print("=" * 60)
    operations = restructure_mci(source_path, output_path, dry_run=False)
    print(f"\nRestructured {len(operations)} files")

    # Step 2: Parse all recordings
    print("\n" + "=" * 60)
    print("STEP 2: Parsing raw EmotiBit data")
    print("=" * 60)
    counts = parse_all_recordings(emotibit_path, parser_path)
    print(f"\nParsing summary: {counts['parsed']} parsed, {counts['failed']} failed")

    # Step 3: Load and compute stats for all recordings
    print("\n" + "=" * 60)
    print("STEP 3: Loading and computing descriptive statistics")
    print("=" * 60)
    recordings = discover_recordings(emotibit_path)
    print(f"Found {len(recordings)} recordings\n")

    all_stats = []
    for r in recordings:
        print(f"  Processing: {r.day}/{r.participant}")
        data = load_recording(r.path, r.timestamp)
        if not data:
            print("    No sensor data loaded, skipping")
            continue

        stats_df = compute_recording_stats(data)
        stats_df["day"] = r.day
        stats_df["participant"] = r.participant
        all_stats.append(stats_df)

    if not all_stats:
        print("No recordings loaded successfully")
        return

    # Step 4: Save results
    print("\n" + "=" * 60)
    print("STEP 4: Saving results")
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
    if len(sys.argv) != 4:
        print(
            "Usage: python src/MCI/main.py "
            "<dataparser_path> <source_path> <output_path>"
        )
        sys.exit(1)

    parser_path = Path(sys.argv[1])
    source_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])

    if not parser_path.exists():
        print(f"Error: DataParser not found at {parser_path}")
        sys.exit(1)

    if not source_path.exists():
        print(f"Error: Source path not found at {source_path}")
        sys.exit(1)

    main(parser_path, source_path, output_path)
