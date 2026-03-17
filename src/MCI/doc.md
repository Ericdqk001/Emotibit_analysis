# MCI EmotiBit Pipeline

Loads parsed EmotiBit sensor data for the INTACT-MCI cohort and computes descriptive statistics.

## Usage

```bash
python src/MCI/main.py data/INTACT-MCI_restructured
```

## Pipeline Steps (`main.py`)

1. **Load and compute stats** - Discovers all recordings under `data_path/emotibit/`, loads sensor CSVs, computes descriptive statistics per participant per day.
2. **Save results** - Outputs `mci_descriptive_stats.csv` with columns: day, participant, sensor, n_samples, duration_s, sampling_rate_hz, mean, std, min, q25, median, q75, max.

> **Note:** The automated parsing step was removed from the pipeline as it caused the DataParser software to terminate early. Parsing was done manually using the EmotiBit DataParser GUI instead.

## Scripts

### `scripts/load.py`

- `RecordingInfo` - Dataclass holding metadata for one recording (participant, day, path, timestamp).
- `discover_recordings(base_path)` - Scans `day*/INTACT-MCI-*/` directories, finds parsed sensor CSVs, returns list of `RecordingInfo`.
- `load_sensor(csv_path)` - Loads a single parsed sensor CSV, converts `LocalTimestamp` to UTC datetime and relative `Time_s`. Uses `pd.to_numeric` with `errors="coerce"` on `LocalTimestamp` to handle malformed values.
- `load_recording(recording_path, timestamp, sensors)` - Loads all sensor files (HR, EA, PG) for one recording, returns dict mapping sensor name to DataFrame.

### `scripts/describe.py`

- `compute_sensor_stats(df, value_col)` - Computes descriptive statistics (mean, std, min, max, median, q25, q75, n_samples, duration, sampling rate) for one sensor column. Uses `pd.to_numeric(errors="coerce")` to handle mixed int/str types from chunked CSV reading.
- `compute_recording_stats(data)` - Calls `compute_sensor_stats` for each sensor in a recording, returns a combined DataFrame. Includes error handling to identify problematic participant/sensor combinations.

## Output

- `output/mci_descriptive_stats.csv`
