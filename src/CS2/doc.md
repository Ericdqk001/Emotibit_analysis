# CS2 EmotiBit Pipeline

Computes descriptive statistics for INTACT-CS2 EmotiBit sensor data (HR, EA, PG).

## Usage

```bash
python src/CS2/main.py data/INTACT-CS2_restructured
```

**Prerequisites:** Data must be restructured (via `src/data_structure/`) and parsed (manually via EmotiBit DataParser GUI) before running.

## Pipeline

1. **Load** — discovers all recordings under `data_path/emotibit/`, loads parsed sensor CSVs
2. **Save** — outputs `output/emotibit_CS2_descriptive_stats.csv`

Output columns: `day, pair, participant, sensor, n_samples, duration_s, sampling_rate_hz, mean, std, min, q25, median, q75, max`

## Scripts

- **`scripts/load.py`** — discovers recordings in `day*/Pair*/participant/` structure, loads sensor CSVs with timestamp conversion
- **`scripts/describe.py`** — computes descriptive statistics per sensor per recording
- **`scripts/parse.py`** — automated parsing via EmotiBit DataParser (not used in pipeline; parsing is done manually as the automated approach caused early termination)
