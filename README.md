# Setting up

## Install uv

* On Windows
`powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

* On macOS
`curl -LsSf https://astral.sh/uv/install.sh | sh`

## Install 🤖 Just a command runner

* On Windows
`winget install --id Casey.Just --exact`

* On macOS
`brew install just`

## Run (in a new CLI)

`just setup`

## Get CS2 emotibit descriptive statistics

```bash
python src/emotibit/main.py <dataparser_path> <data_path>
```

Results saved to `src/emotibit/output/emotibit_descriptive_stats.csv`.

### DataParser path

macOS:
```
/Users/<username>/EmotiBitSoftware_v1/EmotiBitDataParser.app/Contents/MacOS/EmotiBitDataParser
```

Windows:
```
C:\EmotiBitSoftware\EmotiBitDataParser.exe
```

### Data path

macOS (mounted datastore):
```
/Volumes/INT-ACT/INTACT-CS2_restructured/emotibit
```

Windows (mapped drive):
```
Z:\INTACT-CS2_restructured\emotibit
```

### Full example (macOS)

```bash
python src/emotibit/main.py \
    ~/EmotiBitSoftware_v1/EmotiBitDataParser.app/Contents/MacOS/EmotiBitDataParser \
    /Volumes/INT-ACT/INTACT-CS2_restructured/emotibit
```

### Full example (Windows)

```bash
python src/emotibit/main.py ^
    C:\EmotiBitSoftware\EmotiBitDataParser.exe ^
    Z:\INTACT-CS2_restructured\emotibit
```

## Get MCI emotibit descriptive statistics

```bash
python src/MCI/main.py <dataparser_path> <source_path> <output_path>
```

- `source_path`: flat folder with raw MCI emotibit files
- `output_path`: where the restructured data will be written

The pipeline restructures the flat files into `day*/INTACT-MCI-XX/` folders, then parses, loads, and computes descriptive statistics.

Results saved to `src/MCI/output/mci_descriptive_stats.csv`.

### Source path (flat folder)

macOS (mounted datastore):
```
/Volumes/INT-ACT/INTACT-MCI/emotibit
```

Windows (mapped drive):
```
Z:\INTACT-MCI\emotibit
```

### Output path (restructured folder)

macOS:
```
/Volumes/INT-ACT/INTACT-MCI_restructured
```

Windows:
```
Z:\INTACT-MCI_restructured
```

### Full example (macOS)

```bash
python src/MCI/main.py \
    ~/EmotiBitSoftware_v1/EmotiBitDataParser.app/Contents/MacOS/EmotiBitDataParser \
    /Volumes/INT-ACT/INTACT-MCI/emotibit \
    /Volumes/INT-ACT/INTACT-MCI_restructured
```

### Full example (Windows)

```bash
python src/MCI/main.py ^
    C:\EmotiBitSoftware\EmotiBitDataParser.exe ^
    Z:\INTACT-MCI\emotibit ^
    Z:\INTACT-MCI_restructured
```
