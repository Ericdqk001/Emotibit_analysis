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


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        test_path = Path(sys.argv[1])
        success = parse_with_dataparser(test_path)
        print(f"\nResult: {'Success' if success else 'Failed'}")
    else:
        print("Usage: python parse_raw_data.py <raw_csv_path>")
        print("\nExample:")
        print(
            "  python parse_raw_data.py /Volumes/INT-ACT/INTACT-CS2_restructured/"
            "emotibit/day1/Pair1/O-12/2025-10-13_14-49-24-526653.csv"
        )
