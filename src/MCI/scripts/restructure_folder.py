"""Restructure INTACT-MCI emotibit data.

From: flat folder with files like 2025-10-16_MCI-04-Day1.csv
To:   emotibit/day1/INTACT-MCI-04/{timestamp}.csv

Timestamp is extracted from the first line of each CSV file.
"""

import re
import shutil
from pathlib import Path


def extract_timestamp_from_csv(csv_path: Path) -> str | None:
    """Extract timestamp from the first line of a CSV file.

    The first line format: "3321574,35552,1,RB,1,100,2025-10-13_14-49-24-526653"
    Returns the last field (timestamp).
    """
    with open(csv_path) as f:
        first_line = f.readline().strip()

    fields = first_line.split(",")
    if fields:
        timestamp = fields[-1]
        if re.match(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d+", timestamp):
            return timestamp
    return None


def parse_mci_filename(filename: str) -> dict | None:
    """Parse MCI filename to extract participant ID and day.

    Examples:
        2025-10-16_MCI-04-Day1.csv -> {id: "04", day: "day1"}
        2025-10-17_MCI-04-Day2-Part1.csv -> {id: "04", day: "day2"}
    """
    match = re.match(
        r"\d{4}-\d{2}-\d{2}_MCI-(\d+)-Day(\d+)",
        filename,
    )
    if not match:
        return None

    return {
        "id": match.group(1),
        "day": f"day{match.group(2)}",
    }


def concatenate_csvs(csv_paths: list[Path], dest_path: Path) -> None:
    """Concatenate multiple raw EmotiBit CSVs into one file.

    Raw EmotiBit CSVs have variable column counts per row, so we concatenate
    them as raw text rather than parsing as structured DataFrames.
    """
    with open(dest_path, "w") as outfile:
        for csv_path in csv_paths:
            with open(csv_path) as infile:
                outfile.write(infile.read())


def restructure_mci(
    source_path: Path, output_path: Path, dry_run: bool = True
) -> list[dict]:
    """Restructure MCI emotibit data.

    Args:
        source_path: Path to flat folder with MCI emotibit files
        output_path: Path to output folder (e.g., INTACT-MCI_restructured)
        dry_run: If True, only print what would happen

    Returns:
        List of operations performed
    """
    operations = []

    # MCI-04 Day2 has Part1 and Part2 (recording was interrupted).
    # Collect those files to concatenate them into one.
    mci04_day2_parts: list[Path] = []

    for file in sorted(source_path.iterdir()):
        if file.name.startswith("."):
            continue

        # Process CSV files (skip _info.json, handle separately)
        if file.suffix == ".csv":
            info = parse_mci_filename(file.name)
            if not info:
                print(f"Warning: Could not parse filename: {file.name}")
                continue

            # Collect MCI-04 Day2 parts for concatenation
            if info["id"] == "04" and info["day"] == "day2":
                mci04_day2_parts.append(file)
                continue

            timestamp = extract_timestamp_from_csv(file)
            if not timestamp:
                print(f"Warning: Could not extract timestamp: {file.name}")
                continue

            participant = f"INTACT-MCI-{info['id']}"
            dest_dir = output_path / "emotibit" / info["day"] / participant
            dest_csv = dest_dir / f"{timestamp}.csv"

            # Also handle matching _info.json
            info_file = file.with_name(file.stem + "_info.json")
            dest_json = dest_dir / f"{timestamp}_info.json"

            if not dry_run:
                dest_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, dest_csv)
                if info_file.exists():
                    shutil.copy2(info_file, dest_json)

            print(f"  {file.name}")
            print(f"    -> {dest_csv.relative_to(output_path)}")

            operations.append(
                {
                    "source": str(file),
                    "dest": str(dest_csv),
                    "participant": participant,
                    "day": info["day"],
                    "timestamp": timestamp,
                }
            )

    # Concatenate MCI-04 Day2 Part1 + Part2
    if mci04_day2_parts:
        mci04_day2_parts.sort()  # Part1 before Part2
        timestamp = extract_timestamp_from_csv(mci04_day2_parts[0])
        if not timestamp:
            print("Warning: Could not extract timestamp for MCI-04 Day2")
        else:
            participant = "INTACT-MCI-04"
            dest_dir = output_path / "emotibit" / "day2" / participant
            dest_csv = dest_dir / f"{timestamp}.csv"

            if not dry_run:
                dest_dir.mkdir(parents=True, exist_ok=True)
                concatenate_csvs(mci04_day2_parts, dest_csv)

                # Copy _info.json from Part1
                info_file = mci04_day2_parts[0].with_name(
                    mci04_day2_parts[0].stem + "_info.json"
                )
                if info_file.exists():
                    dest_json = dest_dir / f"{timestamp}_info.json"
                    shutil.copy2(info_file, dest_json)

            part_names = [p.name for p in mci04_day2_parts]
            print(f"  {' + '.join(part_names)} (concatenated)")
            print(f"    -> {dest_csv.relative_to(output_path)}")

            operations.append(
                {
                    "source": str(mci04_day2_parts),
                    "dest": str(dest_csv),
                    "participant": participant,
                    "day": "day2",
                    "timestamp": timestamp,
                }
            )

    return operations


if __name__ == "__main__":
    source_path = Path("/Volumes/INT-ACT/INTACT-MCI/emotibit")
    output_path = Path("/Volumes/INT-ACT/INTACT-MCI_restructured")

    if not source_path.exists():
        print(f"Error: {source_path} not found. Is the volume mounted?")
        exit(1)

    print("Restructuring...")
    operations = restructure_mci(source_path, output_path, dry_run=False)
    print(f"\nDone. {len(operations)} files copied to {output_path}")
