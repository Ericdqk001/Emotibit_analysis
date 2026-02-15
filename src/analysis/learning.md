# EmotiBit Analysis: Learning Notes for Descriptive Analysis

## 1. Data Loading (`loading_data.py`)

**Key function:** `load_emotibit_sensor(input_csv, sensor_type)`

- Extracts start time from filename format: `YYYY-MM-DD_HH-MM-SS-ffffff_SENSOR.csv` (line 18-29)
- Filters data by `TypeTag` column to isolate specific sensor (line 37-38)
- Converts `LocalTimestamp` (Unix seconds) to UTC datetime as `AbsoluteTime` (line 47-49)
- Creates relative `Time_s` column for time-series plotting (line 52-53)

**Sensor types available:** HR, AX, AY, AZ, PG, EA, EL, T1, TH, etc.

---

## 2. Descriptive Statistics (`emotibit_task_analysis.py`)

**Key function:** `calculate_task_stats(df, task_file, value_col)`

**Statistics computed per task window (lines 114-123):**
- Mean
- Standard deviation (ddof=1)
- Min, Max
- Median
- Mode (via `scipy.stats.mode`)
- Sample count

**Task segmentation approach (lines 36-109):**
- Reads task timing file (semicolon-separated) with columns: `ID`, `date`, `task1_st`, `task1_et`, etc.
- Parses start/end times with timezone handling (Europe/London → UTC)
- Filters dataframe by `AbsoluteTime` within task window

---

## 3. Statistical Testing (`stat_test.py`)

**Key function:** `calculate_task_ttests(df, task_file, value_col, subject_id)`

**Performs paired t-tests between tasks (lines 97-124):**
- Task1 vs Task2, Task1 vs Task3, Task2 vs Task3
- Uses `scipy.stats.ttest_rel` (paired t-test)
- Computes Cohen's d effect size: `mean(diff) / std(diff)` (lines 109-111)
- Truncates arrays to equal length for pairing (lines 101-105)

---

## 4. Multi-Subject Processing (`wrist.py`)

**Key function:** `process_wrist_sensor_data(sensor_type, task_file, subject_ids, base_folder)`

**Workflow (lines 26-48):**
1. Loop through subject folders
2. Load sensor CSV with `load_emotibit_sensor`
3. Calculate task stats with `calculate_task_stats`
4. Run t-tests with `calculate_task_ttests`
5. Combine results, filling missing values across subjects

---

## 5. Visualization (`HR.ipynb`)

**Basic time-series plot (cell `02a43229`):**
```python
plt.plot(df["Time_s"], df["HR"])
plt.xlabel("Time (seconds)")
plt.ylabel("Heart Rate (bpm)")
```

---

## 6. Task Timing File Format

From `stat_test.py` lines 26-34, the expected format:
```
ID;date;task1_st;task1_et;task2_st;task2_et;task3_st;task3_et
SL;2025-05-12;22:07:31;22:50:02;22:52:00;23:14:50;...
```

---

## Summary: Key Steps for Descriptive Analysis

1. **Load data** with `load_emotibit_sensor()` specifying sensor type
2. **Segment by task** using task timing file
3. **Compute descriptives**: mean, std, min, max, median, mode, n
4. **Compare tasks** with paired t-tests + Cohen's d
5. **Visualize** time-series with matplotlib
