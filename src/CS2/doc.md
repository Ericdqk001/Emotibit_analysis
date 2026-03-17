# CS2 EmotiBit Pipeline

Loads parsed EmotiBit sensor data for the INTACT-CS2 cohort and computes descriptive statistics.

## Usage

```bash
python src/CS2/main.py . data/INTACT-CS2_restructured/emotibit
```

## Pipeline Steps (`main.py`)

1. **Load and compute stats** - Discovers all recordings, loads sensor CSVs, computes descriptive statistics per participant per day.
2. **Save results** - Outputs `emotibit_CS2_descriptive_stats.csv` with columns: day, pair, participant, sensor, n_samples, duration_s, sampling_rate_hz, mean, std, min, q25, median, q75, max.

> **Note:** The automated parsing step was removed from the pipeline as it caused the DataParser software to terminate early. Parsing was done manually using the EmotiBit DataParser GUI instead.

## Scripts

### `scripts/load.py`

- `RecordingInfo` - Dataclass holding metadata for one recording (pair_id, participant, day, path, timestamp).
- `discover_recordings(base_path)` - Scans `day*/Pair*/participant/` directories, finds parsed sensor CSVs, returns list of `RecordingInfo`.
- `load_sensor(csv_path)` - Loads a single parsed sensor CSV, converts `LocalTimestamp` to UTC datetime and relative `Time_s`.
- `load_recording(recording_path, timestamp, sensors)` - Loads all sensor files (HR, EA, PG) for one recording, returns dict mapping sensor name to DataFrame.

### `scripts/describe.py`

- `compute_sensor_stats(df, value_col)` - Computes descriptive statistics (mean, std, min, max, median, q25, q75, n_samples, duration, sampling rate) for one sensor column.
- `compute_recording_stats(data)` - Calls `compute_sensor_stats` for each sensor in a recording, returns a combined DataFrame.

### `scripts/parse.py`

- `parse_with_dataparser(raw_csv_path, parser_path)` - Calls the EmotiBit DataParser executable on a raw CSV file.
- `parse_all_recordings(base_path, parser_path)` - Batch-parses all raw recordings in the directory.

## Output

- `output/emotibit_CS2_descriptive_stats.csv`
