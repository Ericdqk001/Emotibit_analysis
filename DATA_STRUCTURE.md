# INTACT-CS2 Restructured Data Structure

This document describes the folder structure of the restructured INTACT-CS2 dataset located at `/Volumes/INT-ACT/INTACT-CS2_restructured/`.

## Overview

The data is organized by **modality** (emotibit, audio, surveys), then by **day** (day1, day2), and for emotibit and audio, further by **pair** and **participant_type-ID** (Type as in "O" or "Y").

```
INTACT-CS2_restructured/
├── emotibit/
│   ├── day1/
│   │   ├── Pair1/
│   │   │   ├── O-12/
│   │   │   │   ├── {timestamp}.csv
│   │   │   │   └── {timestamp}_info.json
│   │   │   └── Y-06/
│   │   ├── Pair2/
│   │   │   ├── O-03/
│   │   │   └── Y-05/
│   │   └── ...
│   └── day2/
│       └── (same structure)
├── audio/
│   ├── day1/
│   │   ├── Pair1/
│   │   │   ├── O-12/
│   │   │   │   └── sync_timestamp.wav
│   │   │   └── Y-06/
│   │   └── ...
│   └── day2/
│       └── (same structure)
└── surveys/
    ├── day1/
    │   └── *.xlsx
    └── day2/
        └── *.xlsx
```

## Notes

- Original data preserved at `/Volumes/INT-ACT/INTACT-CS2/`
- Metadata source: `metadata.json`, which documents information on participant ID pairs and date.
- The audio data were copied from `/Volumes/INT-ACT/INTACT-CS2/` instead of `/Volumes/INT-ACT/audio`, therefore only day2 is populated. Furthermore, the names of the audio files are all named `sync_timestamps.wav` for now, which can later be renamed to indicate the synchronization time stamp with the emotibit data.
