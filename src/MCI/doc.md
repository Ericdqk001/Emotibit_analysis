# MCI EmotiBit Pipeline

Computes descriptive statistics for INTACT-MCI EmotiBit sensor data (HR, EA, PG).

## Usage

```bash
python src/MCI/main.py data/INTACT-MCI_restructured
```

**Prerequisites:** Data must be restructured (via `src/data_structure/`) and parsed (manually via EmotiBit DataParser GUI) before running.

## Pipeline

1. **Load** — discovers all recordings under `data_path/emotibit/`, loads parsed sensor CSVs
2. **Save** — outputs `output/mci_descriptive_stats.csv`

Output columns: `day, participant, sensor, n_samples, duration_s, sampling_rate_hz, mean, std, min, q25, median, q75, max`

## Scripts

- **`scripts/load.py`** — discovers recordings in `day*/INTACT-MCI-*/` structure, loads sensor CSVs with timestamp conversion
- **`scripts/describe.py`** — computes descriptive statistics per sensor per recording; handles mixed int/str types from chunked CSV reading via `pd.to_numeric(errors="coerce")`
