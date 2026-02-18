"""Parse raw EmotiBit CSV data using the DataParser app.

Calls the EmotiBit DataParser GUI app to convert raw CSV files
into separate sensor files.
"""

import subprocess
from pathlib import Path

# Path to the EmotiBit DataParser executable (inside .app bundle)
DATAPARSER_PATH = Path(
    "/Users/qingkundeng/Desktop/EmotiBitSoftware_v1/"
    "EmotiBitDataParser.app/Contents/MacOS/EmotiBitDataParser"
)


def parse_with_dataparser(raw_csv_path: Path, timeout: int | None = None) -> bool:
    """Call EmotiBit DataParser app with the raw file.

    Args:
        raw_csv_path: Path to the raw EmotiBit CSV file.
        timeout: Maximum seconds to wait for parsing.

    Returns:
        True if parsing succeeded, False otherwise.
    """
    if not DATAPARSER_PATH.exists():
        print(f"DataParser not found at: {DATAPARSER_PATH}")
        return False

    if not raw_csv_path.exists():
        print(f"Raw file not found: {raw_csv_path}")
        return False

    print(f"Parsing: {raw_csv_path.name}")

    try:
        result = subprocess.run(
            [str(DATAPARSER_PATH), str(raw_csv_path)],
            timeout=timeout,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("  Parsing complete")
            return True
        else:
            print(f"  DataParser error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"  DataParser timed out after {timeout}s")
        return False
    except Exception as e:
        print(f"  Error running DataParser: {e}")
        return False


def parse_all_recordings(base_path: Path, timeout: int | None = None) -> dict:
    """Parse all unparsed EmotiBit recordings.

    For each participant folder, check if any parsed sensor files exist.
    If not, parse the raw CSV.

    Args:
        base_path: Base path to emotibit folder
        timeout: Maximum seconds to wait for parsing each file

    Returns:
        Dict with counts: parsed, skipped, failed
    """
    counts = {"parsed": 0, "skipped": 0, "failed": 0}

    for day_dir in sorted(base_path.glob("day*")):
        for pair_dir in sorted(day_dir.glob("Pair*")):
            for participant_dir in sorted(pair_dir.glob("*-*")):
                # Check if any parsed sensor files exist (e.g., *_HR.csv, *_EA.csv)
                has_parsed_files = (
                    list(participant_dir.glob("*_HR.csv"))
                    or list(participant_dir.glob("*_EA.csv"))
                    or list(participant_dir.glob("*_PG.csv"))
                )

                if has_parsed_files:
                    print(f"Already parsed: {participant_dir.relative_to(base_path)}")
                    counts["skipped"] += 1
                    continue

                # Find raw CSV (timestamp only, 1 underscore)
                raw_csv = [
                    f for f in participant_dir.glob("*.csv") if f.stem.count("_") == 1
                ]

                if not raw_csv:
                    print(f"No raw CSV found: {participant_dir.relative_to(base_path)}")
                    continue

                # Parse it
                success = parse_with_dataparser(raw_csv[0], timeout=timeout)
                if success:
                    counts["parsed"] += 1
                else:
                    counts["failed"] += 1

    return counts


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        path = Path(sys.argv[1])

        # Check if it's a single file or a directory
        if path.is_file():
            success = parse_with_dataparser(path)
            print(f"\nResult: {'Success' if success else 'Failed'}")
        elif path.is_dir():
            print(f"Batch parsing all recordings in: {path}\n")
            counts = parse_all_recordings(path)
            print("\nSummary:")
            print(f"  Parsed: {counts['parsed']}")
            print(f"  Skipped: {counts['skipped']}")
            print(f"  Failed: {counts['failed']}")
        else:
            print(f"Error: {path} is not a file or directory")
    else:
        print("Usage: python parse_raw_data.py <path>")
        print("\nSingle file:")
        print(
            "  python parse_raw_data.py "
            "/Volumes/INT-ACT/INTACT-CS2_restructured/emotibit/day1/Pair1/O-12/2025-10-13_14-49-24-526653.csv"
        )
        print("\nBatch (all recordings):")
        print(
            "  python parse_raw_data.py "
            "/Volumes/INT-ACT/INTACT-CS2_restructured/emotibit"
        )
