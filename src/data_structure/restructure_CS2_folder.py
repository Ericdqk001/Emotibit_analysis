import json
import re
import shutil
from pathlib import Path


def generate_metadata(intact_cs2_path: Path) -> dict:
    """Scan INTACT-CS2 folder and generate metadata structure."""
    pairs = []

    # Scan all pair folders
    pair_folders = sorted(
        [d for d in intact_cs2_path.iterdir() if d.is_dir() and "Pair" in d.name]
    )

    for pair_folder in pair_folders:
        pair_match = re.search(r"Pair(\d+)", pair_folder.name)
        if not pair_match:
            continue

        pair_id = f"Pair{pair_match.group(1)}"

        # Find all CSV files in this pair folder
        csv_files = list(pair_folder.rglob("*.csv"))

        o_participant = None
        y_participant = None
        day_1_date = None
        day_2_date = None

        for csv_file in csv_files:
            # Skip macOS artifact files
            if csv_file.name.startswith("._"):
                continue

            # Extract participant ID
            o_match = re.search(r"O-(\d+)", csv_file.name)
            y_match = re.search(r"Y-(\d+)", csv_file.name)

            if o_match and o_participant is None:
                o_participant = o_match.group(1)
            elif y_match and y_participant is None:
                y_participant = y_match.group(1)

            # Extract date from filename
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", csv_file.name)
            if date_match:
                date = date_match.group(1)

                # Determine if Day1 or Day2
                if "Day1" in csv_file.name or "DAY1" in csv_file.name:
                    if day_1_date is None:
                        day_1_date = date
                elif "Day2" in csv_file.name or "DAY2" in csv_file.name:
                    if day_2_date is None:
                        day_2_date = date

        # Add pair if we found all required info
        if o_participant and y_participant and day_1_date and day_2_date:
            pairs.append(
                {
                    "pair_id": pair_id,
                    "O": o_participant,
                    "Y": y_participant,
                    "day_1_date": day_1_date,
                    "day_2_date": day_2_date,
                }
            )

    return {"pairs": pairs}


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
        # Validate it looks like a timestamp (YYYY-MM-DD_HH-MM-SS-MMMMMM)
        if re.match(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d+", timestamp):
            return timestamp
    return None


def extract_date_from_filename(filename: str) -> str | None:
    """Extract date (YYYY-MM-DD) from a filename."""
    match = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
    return match.group(1) if match else None


def extract_participant_from_filename(filename: str) -> tuple[str, str] | None:
    """Extract participant type (O/Y) and ID from filename.

    Returns tuple of (type, id) e.g., ("O", "12") or ("Y", "06")
    """
    # Try patterns like O-12, Y-06, O-03, etc.
    match = re.search(r"([OY])-(\d+)", filename)
    if match:
        return (match.group(1), match.group(2))
    return None


def find_pair_for_participant(
    metadata: dict, participant_type: str, participant_id: str
) -> dict | None:
    """Find the pair that contains this participant."""
    for pair in metadata["pairs"]:
        if pair[participant_type] == participant_id:
            return pair
    return None


def determine_day(metadata_pair: dict, date: str) -> str | None:
    """Determine if a date corresponds to day1 or day2 for a pair."""
    if date == metadata_pair["day_1_date"]:
        return "day1"
    elif date == metadata_pair["day_2_date"]:
        return "day2"
    return None


def should_skip_file(filename: str) -> bool:
    """Check if file should be skipped (macOS artifacts)."""
    return filename.startswith(".") or filename.startswith("._")


def restructure_data(
    source_path: Path,
    surveys_path: Path,
    output_path: Path,
    metadata: dict,
    dry_run: bool = True,
) -> list[dict]:
    """Restructure the data into the new folder structure.

    Returns a list of operations performed (for logging/verification).
    """
    operations = []

    # Create base output directories
    modalities = ["audio", "emotibit", "surveys"]
    days = ["day1", "day2"]

    if not dry_run:
        output_path.mkdir(parents=True, exist_ok=True)

    # Create folder structure
    for modality in modalities:
        for day in days:
            if modality == "surveys":
                # Surveys don't have pair subfolders
                dir_path = output_path / modality / day
            else:
                # Create pair and participant folders
                for pair in metadata["pairs"]:
                    pair_id = pair["pair_id"]
                    o_id = f"O-{pair['O']}"
                    y_id = f"Y-{pair['Y']}"

                    for participant_id in [o_id, y_id]:
                        dir_path = (
                            output_path / modality / day / pair_id / participant_id
                        )
                        if not dry_run:
                            dir_path.mkdir(parents=True, exist_ok=True)
                        operations.append({"type": "mkdir", "path": str(dir_path)})

    # Process surveys (simple copy with day organization)
    operations.extend(_process_surveys(surveys_path, output_path, dry_run))

    # Process INTACT-CS2 data (emotibit and audio)
    operations.extend(_process_intact_cs2(source_path, output_path, metadata, dry_run))

    return operations


def _process_surveys(
    surveys_path: Path, output_path: Path, dry_run: bool
) -> list[dict]:
    """Process and copy survey files."""
    operations = []

    if not surveys_path.exists():
        print(f"Warning: Surveys path does not exist: {surveys_path}")
        return operations

    for file in surveys_path.iterdir():
        if should_skip_file(file.name):
            continue

        # Determine day from filename (handle day1, day_1, day-1 patterns)
        name_lower = file.name.lower()
        if "day1" in name_lower or "day_1" in name_lower or "day-1" in name_lower:
            day = "day1"
        elif "day2" in name_lower or "day_2" in name_lower or "day-2" in name_lower:
            day = "day2"
        else:
            print(f"Warning: Could not determine day for survey: {file.name}")
            continue

        dest_dir = output_path / "surveys" / day
        dest_path = dest_dir / file.name

        if not dry_run:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, dest_path)

        operations.append(
            {
                "type": "copy",
                "source": str(file),
                "dest": str(dest_path),
                "modality": "surveys",
            }
        )

    return operations


def _process_intact_cs2(
    source_path: Path, output_path: Path, metadata: dict, dry_run: bool
) -> list[dict]:
    """Process INTACT-CS2 emotibit and audio files."""
    operations = []

    if not source_path.exists():
        print(f"Warning: Source path does not exist: {source_path}")
        return operations

    # Iterate through pair folders
    for pair_folder in source_path.iterdir():
        if not pair_folder.is_dir() or should_skip_file(pair_folder.name):
            continue

        # Extract pair number
        pair_match = re.search(r"Pair(\d+)", pair_folder.name)
        if not pair_match:
            continue

        pair_id = f"Pair{pair_match.group(1)}"

        # Find matching metadata
        pair_metadata = None
        for pair in metadata["pairs"]:
            if pair["pair_id"] == pair_id:
                pair_metadata = pair
                break

        if not pair_metadata:
            print(f"Warning: No metadata found for {pair_id}")
            continue

        # Process all files in the pair folder (recursively)
        for file in pair_folder.rglob("*"):
            if not file.is_file() or should_skip_file(file.name):
                continue

            # Process based on file type
            if file.suffix.lower() == ".csv" and "_info" not in file.name:
                ops = _process_emotibit_csv(
                    file, output_path, pair_id, pair_metadata, dry_run
                )
                operations.extend(ops)
            elif file.suffix.lower() == ".json":
                ops = _process_emotibit_json(
                    file, output_path, pair_id, pair_metadata, dry_run
                )
                operations.extend(ops)
            elif file.suffix.lower() == ".wav":
                ops = _process_audio(file, output_path, pair_id, pair_metadata, dry_run)
                operations.extend(ops)

    return operations


def _process_emotibit_csv(
    file: Path,
    output_path: Path,
    pair_id: str,
    pair_metadata: dict,
    dry_run: bool,
) -> list[dict]:
    """Process an emotibit CSV file."""
    operations = []

    # Extract participant info from filename first
    participant = extract_participant_from_filename(file.name)

    # If not in filename, try to get from parent folder (Pair1 style)
    if not participant:
        participant = extract_participant_from_filename(file.parent.name)

    if not participant:
        print(f"Warning: Could not extract participant from: {file.name}")
        return operations

    participant_type, participant_id = participant

    # Verify participant belongs to this pair
    if pair_metadata[participant_type] != participant_id:
        print(f"Warning: {participant_type}-{participant_id} not in {pair_id}")
        return operations

    # Extract date and determine day
    date = extract_date_from_filename(file.name)
    if not date:
        print(f"Warning: Could not extract date from: {file.name}")
        return operations

    day = determine_day(pair_metadata, date)
    if not day:
        print(f"Warning: Date {date} doesn't match day1/day2 for {pair_id}")
        return operations

    # Extract timestamp from CSV content
    timestamp = extract_timestamp_from_csv(file)
    if not timestamp:
        print(f"Warning: Could not extract timestamp from CSV: {file.name}")
        return operations

    # Build destination path
    participant_folder = f"{participant_type}-{participant_id}"
    dest_dir = output_path / "emotibit" / day / pair_id / participant_folder
    dest_filename = f"{timestamp}.csv"
    dest_path = dest_dir / dest_filename

    if not dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, dest_path)

    operations.append(
        {
            "type": "copy",
            "source": str(file),
            "dest": str(dest_path),
            "modality": "emotibit",
            "day": day,
            "pair": pair_id,
            "participant": participant_folder,
            "timestamp": timestamp,
        }
    )

    return operations


def _process_emotibit_json(
    file: Path,
    output_path: Path,
    pair_id: str,
    pair_metadata: dict,
    dry_run: bool,
) -> list[dict]:
    """Process an emotibit JSON info file."""
    operations = []

    # Extract participant info from filename first
    participant = extract_participant_from_filename(file.name)

    # If not in filename, try to get from parent folder (Pair1 style)
    if not participant:
        participant = extract_participant_from_filename(file.parent.name)

    if not participant:
        print(f"Warning: Could not extract participant from: {file.name}")
        return operations

    participant_type, participant_id = participant

    # Verify participant belongs to this pair
    if pair_metadata[participant_type] != participant_id:
        print(f"Warning: {participant_type}-{participant_id} not in {pair_id}")
        return operations

    # Extract date and determine day
    date = extract_date_from_filename(file.name)
    if not date:
        print(f"Warning: Could not extract date from: {file.name}")
        return operations

    day = determine_day(pair_metadata, date)
    if not day:
        print(f"Warning: Date {date} doesn't match day1/day2 for {pair_id}")
        return operations

    # Try to extract full timestamp from filename
    # Pattern: 2025-10-13_14-49-24-526653_info.json (Pair1 style)
    timestamp_match = re.search(r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d+)", file.name)

    if timestamp_match:
        timestamp = timestamp_match.group(1)
    else:
        # For Pair2-6 style: find matching CSV and extract timestamp from it
        # JSON: 2025-11-25_CS2-Pair3-Y-11-Day1_info.json
        # CSV:  2025-11-25_CS2-Pair3-Y-11-Day1.csv
        csv_name = file.name.replace("_info.json", ".csv")

        # Hardcoded fix for naming inconsistency in Pair2
        # JSON: 2025-11-13_CS2-Pair2-O-03_info.json
        # CSV:  2025-11-13_CS2-Pair2-O-03-Day1.csv (missing -Day1 in JSON name)
        if csv_name == "2025-11-13_CS2-Pair2-O-03.csv":
            csv_name = "2025-11-13_CS2-Pair2-O-03-Day1.csv"
        csv_path = file.parent / csv_name
        if csv_path.exists():
            timestamp = extract_timestamp_from_csv(csv_path)
            if not timestamp:
                print(f"Warning: Could not extract timestamp from CSV: {csv_name}")
                return operations
        else:
            print(f"Warning: No matching CSV for JSON: {file.name}")
            return operations

    # Build destination path
    participant_folder = f"{participant_type}-{participant_id}"
    dest_dir = output_path / "emotibit" / day / pair_id / participant_folder
    dest_filename = f"{timestamp}_info.json"
    dest_path = dest_dir / dest_filename

    if not dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, dest_path)

    operations.append(
        {
            "type": "copy",
            "source": str(file),
            "dest": str(dest_path),
            "modality": "emotibit",
            "day": day,
            "pair": pair_id,
            "participant": participant_folder,
            "timestamp": timestamp,
        }
    )

    return operations


def _process_audio(
    file: Path,
    output_path: Path,
    pair_id: str,
    pair_metadata: dict,
    dry_run: bool,
) -> list[dict]:
    """Process an audio WAV file."""
    operations = []

    # Extract participant info from filename first
    participant = extract_participant_from_filename(file.name)

    # If not in filename, try to get from parent folder
    if not participant:
        participant = extract_participant_from_filename(file.parent.name)

    if not participant:
        print(f"Warning: Could not extract participant from: {file.name}")
        return operations

    participant_type, participant_id = participant

    # Verify participant belongs to this pair
    if pair_metadata[participant_type] != participant_id:
        print(f"Warning: {participant_type}-{participant_id} not in {pair_id}")
        return operations

    # Extract date and determine day
    date = extract_date_from_filename(file.name)
    if not date:
        print(f"Warning: Could not extract date from: {file.name}")
        return operations

    day = determine_day(pair_metadata, date)
    if not day:
        print(f"Warning: Date {date} doesn't match day1/day2 for {pair_id}")
        return operations

    # Build destination path with placeholder name
    participant_folder = f"{participant_type}-{participant_id}"
    dest_dir = output_path / "audio" / day / pair_id / participant_folder
    dest_filename = "sync_timestamp.wav"
    dest_path = dest_dir / dest_filename

    if not dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, dest_path)

    operations.append(
        {
            "type": "copy",
            "source": str(file),
            "dest": str(dest_path),
            "modality": "audio",
            "day": day,
            "pair": pair_id,
            "participant": participant_folder,
        }
    )

    return operations


def print_operations_summary(operations: list[dict]) -> None:
    """Print a summary of operations."""
    copy_ops = [op for op in operations if op["type"] == "copy"]

    print(f"\n{'=' * 60}")
    print("OPERATIONS SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total copy operations: {len(copy_ops)}")

    # Group by modality
    by_modality = {}
    for op in copy_ops:
        modality = op.get("modality", "unknown")
        by_modality[modality] = by_modality.get(modality, 0) + 1

    print("\nBy modality:")
    for modality, count in sorted(by_modality.items()):
        print(f"  {modality}: {count} files")

    print(f"\n{'=' * 60}")
    print("FILE OPERATIONS:")
    print(f"{'=' * 60}")

    for op in copy_ops:
        source = Path(op["source"]).name
        dest = op["dest"]
        print(f"  {source}")
        print(f"    -> {dest}")
        print()


if __name__ == "__main__":
    # Paths
    data_store_path = Path("/", "Volumes", "INT-ACT")
    source_path = data_store_path / "INTACT-CS2"
    surveys_path = data_store_path / "surveys"
    output_path = data_store_path / "INTACT-CS2_restructured"

    # Check paths
    if not source_path.exists():
        print(f"ERROR: Source path does not exist: {source_path}")
        print("Is the volume mounted?")
        exit(1)

    # Generate and save metadata
    metadata = generate_metadata(source_path)
    print(f"Found {len(metadata['pairs'])} pairs")

    metadata_path = source_path / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved metadata to: {metadata_path}")

    # Run in dry-run mode first
    print("\n" + "=" * 60)
    print("DRY RUN MODE - No files will be copied")
    print("=" * 60)

    operations = restructure_data(
        source_path=source_path,
        surveys_path=surveys_path,
        output_path=output_path,
        metadata=metadata,
        dry_run=True,
    )

    print_operations_summary(operations)

    # Ask for confirmation
    print("\n" + "=" * 60)
    response = input("Proceed with actual restructuring? (yes/no): ")

    if response.lower() == "yes":
        print("\nExecuting restructuring...")
        operations = restructure_data(
            source_path=source_path,
            surveys_path=surveys_path,
            output_path=output_path,
            metadata=metadata,
            dry_run=False,
        )
        print("\nRestructuring complete!")
        print(f"Output: {output_path}")
    else:
        print("Aborted.")
