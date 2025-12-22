import pandas as pd
import numpy as np
from datetime import datetime
import pytz
from scipy.stats import ttest_rel

def calculate_task_ttests(df, task_file, value_col='HR', subject_id=None):
    """
    For a single subject, perform paired t-tests between tasks (Task1 vs Task2, Task1 vs Task3, Task2 vs Task3)
    using raw time-series data and the task timings from task_file.

    Args:
        df (pd.DataFrame): Raw dataframe for one subject (must include 'AbsoluteTime' and value_col).
        task_file (str): Path to the task timing file (semicolon-separated).
        value_col (str): Sensor column to test (e.g., 'HR', 'AX').
        subject_id (str): Subject ID to filter from task_file (e.g., 'SL', 'FH').

    Returns:
        pd.DataFrame: One row per task comparison (Task1 vs Task2, etc.) with t-statistic, p-value, sample count, and Cohen's d.
    """

    if subject_id is None:
        raise ValueError("You must provide subject_id for subject-level t-test.")

    # Load and clean task timing file
    df_tasks = pd.read_csv(task_file, sep=';', skipinitialspace=True, header=0, dtype=str, keep_default_na=False)
    df_tasks.columns = [col.strip() for col in df_tasks.columns]
    df_tasks = df_tasks.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Filter for the current subject only
    subject_row = df_tasks[df_tasks['ID'] == subject_id]
    if subject_row.empty:
        print(f"Warning: No task timing info found for subject {subject_id}.")
        return pd.DataFrame()

    row = subject_row.iloc[0]
    date_str = row['date']

    local_tz = pytz.timezone('Europe/London')  # BST
    task_pairs = [('Task1', 'Task2'), ('Task1', 'Task3'), ('Task2', 'Task3')]
    task_data = {}

    # Extract raw data for each task
    for task_num in range(1, 4):
        start_col = f'task{task_num}_st'
        end_col = f'task{task_num}_et'

        st_str = row.get(start_col, '').strip()
        et_str = row.get(end_col, '').strip()

        if st_str == '' or et_str == '':
            task_data[f'Task{task_num}'] = np.array([])
            continue

        # Parse start/end times
        task_start, task_end = pd.NaT, pd.NaT
        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]:
            if pd.isna(task_start):
                try:
                    task_start = datetime.strptime(f"{date_str} {st_str}", fmt)
                except:
                    pass
            if pd.isna(task_end):
                try:
                    task_end = datetime.strptime(f"{date_str} {et_str}", fmt)
                except:
                    pass

        if pd.isna(task_start) or pd.isna(task_end):
            task_data[f'Task{task_num}'] = np.array([])
            continue

        # Convert to UTC
        task_start = local_tz.localize(task_start).astimezone(pytz.utc)
        task_end = local_tz.localize(task_end).astimezone(pytz.utc)

        # Filter data for this task window
        df_task = df[(df['AbsoluteTime'] >= task_start) & (df['AbsoluteTime'] <= task_end)]

        if value_col in df_task.columns:
            values = pd.to_numeric(df_task[value_col].dropna(), errors='coerce').values
            task_data[f'Task{task_num}'] = values
        else:
            task_data[f'Task{task_num}'] = np.array([])

    # Run paired t-tests between task pairs
    results = []
    for task_a, task_b in task_pairs:
        values_a = task_data.get(task_a, np.array([]))
        values_b = task_data.get(task_b, np.array([]))

        min_len = min(len(values_a), len(values_b))

        if min_len >= 2:
            values_a = values_a[:min_len]
            values_b = values_b[:min_len]

            t_stat, p_val = ttest_rel(values_a, values_b, nan_policy='omit')
            diff = values_a - values_b
            cohens_d = diff.mean() / diff.std(ddof=1) if diff.std(ddof=1) != 0 else np.nan
        else:
            t_stat = p_val = cohens_d = np.nan

        results.append({
            'Subject': subject_id,
            'Comparison': f'{task_a}_vs_{task_b}',
            't_statistic': t_stat,
            'p_value': p_val,
            'Cohens_d': cohens_d,
            'n_samples': min_len
        })

    return pd.DataFrame(results)
