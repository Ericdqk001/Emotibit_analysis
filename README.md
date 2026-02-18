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
