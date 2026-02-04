import json
import re
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


if __name__ == "__main__":
    data_store_path = Path("/", "Volumes", "INT-ACT")
    intact_cs2_path = Path(data_store_path, "INTACT-CS2")

    if not intact_cs2_path.exists():
        print("ERROR: Path does not exist. Is the volume mounted?")
    else:
        print("Scanning INTACT-CS2 folder structure...")
        metadata = generate_metadata(intact_cs2_path)

        # Save to file
        output_path = Path("metadata.json")

        with open(output_path, "w") as f:
            json.dump(metadata, f, indent=2)

        print("\nMetadata generated successfully!")
        print(f"Output: {output_path}")
        print(f"\nFound {len(metadata['pairs'])} pairs")
        print("\nPreview:")
        print(json.dumps(metadata, indent=2))
