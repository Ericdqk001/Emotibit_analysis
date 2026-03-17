# Data Structure Scripts

Restructure raw data from the INT-ACT external volume into standardised folder structures for analysis.

**Prerequisites:** Mount the INT-ACT datastore at `/Volumes/INT-ACT` before running any script.

## CS2

```bash
python src/data_structure/restructure_CS2_folder.py
```

Generates metadata (pair assignments, participant IDs, recording dates) from the raw folder, saves `metadata.json` under the source data path, then restructures into `day*/Pair*/participant/` structure with emotibit, audio, and survey files. Runs a dry-run first and asks for confirmation before copying.

## MCI

```bash
python src/data_structure/restructure_MCI_folder.py
```

Restructures flat MCI emotibit data into `emotibit/day*/INTACT-MCI-XX/` structure. No metadata step needed — participant ID and day are parsed directly from filenames. Handles MCI-04 Day2 split recordings (Part1/Part2 concatenated). Runs a dry-run first and asks for confirmation before copying.
