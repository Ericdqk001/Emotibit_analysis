"""Parse raw EmotiBit CSV data using the DataParser app.

Calls the EmotiBit DataParser GUI app to convert raw CSV files
into separate sensor files.
"""

import subprocess
from pathlib import Path


def parse_with_dataparser(
    raw_csv_path: Path, parser_path: Path, timeout: int | None = None
) -> bool:
    """Call EmotiBit DataParser app with the raw file.

    Args:
        raw_csv_path: Path to the raw EmotiBit CSV file.
        parser_path: Path to the EmotiBit DataParser executable.
        timeout: Maximum seconds to wait for parsing.

    Returns:
        True if parsing succeeded, False otherwise.
    """
    if not parser_path.exists():
        print(f"DataParser not found at: {parser_path}")
        return False

    if not raw_csv_path.exists():
        print(f"Raw file not found: {raw_csv_path}")
        return False

    print(f"Parsing: {raw_csv_path.name}")

    try:
        result = subprocess.run(
            [str(parser_path), str(raw_csv_path)],
            timeout=timeout,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            # Verify parsed files exist and are non-empty
            parent = raw_csv_path.parent
            timestamp = raw_csv_path.stem
            empty_files = []
            for sensor in ["HR", "EA", "PG"]:
                sensor_file = parent / f"{timestamp}_{sensor}.csv"
                if not sensor_file.exists():
                    empty_files.append(sensor)
                elif sensor_file.stat().st_size == 0:
                    empty_files.append(sensor)

            if empty_files:
                print(f"  Parsing failed: missing or empty files for {empty_files}")
                return False

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


def parse_all_recordings(
    base_path: Path, parser_path: Path, timeout: int | None = None
) -> dict:
    """Parse all EmotiBit recordings.

    Args:
        base_path: Base path to emotibit folder
        parser_path: Path to the EmotiBit DataParser executable
        timeout: Maximum seconds to wait for parsing each file

    Returns:
        Dict with counts: parsed, failed
    """
    counts = {"parsed": 0, "failed": 0}

    for day_dir in sorted(base_path.glob("day*")):
        for pair_dir in sorted(day_dir.glob("Pair*")):
            for participant_dir in sorted(pair_dir.glob("*-*")):
                # Find raw CSV (timestamp only, 1 underscore)
                raw_csv = [
                    f for f in participant_dir.glob("*.csv") if f.stem.count("_") == 1
                ]

                if not raw_csv:
                    print(f"No raw CSV found: {participant_dir.relative_to(base_path)}")
                    continue

                success = parse_with_dataparser(
                    raw_csv[0], parser_path, timeout=timeout
                )
                if success:
                    counts["parsed"] += 1
                else:
                    counts["failed"] += 1

    return counts


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 2:
        parser_path = Path(sys.argv[1])
        path = Path(sys.argv[2])

        if path.is_file():
            success = parse_with_dataparser(path, parser_path)
            print(f"\nResult: {'Success' if success else 'Failed'}")
        elif path.is_dir():
            print(f"Batch parsing all recordings in: {path}\n")
            counts = parse_all_recordings(path, parser_path)
            print("\nSummary:")
            print(f"  Parsed: {counts['parsed']}")
            print(f"  Failed: {counts['failed']}")
        else:
            print(f"Error: {path} is not a file or directory")
    else:
        print("Usage: python parse.py <dataparser_path> <emotibit_data_path>")
