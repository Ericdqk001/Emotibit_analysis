import pandas as pd
import numpy as np
from datetime import datetime
import pytz
from scipy.stats import mode

def calculate_task_stats(df, task_file, value_col='HR'):
    
    """
    Calculate descriptive statistics (mean, std, min, max, median, mode, samples) 
    for each subject and task for a given EmotiBit value column (e.g., HR, AX, AY).

    Args:
        df (pd.DataFrame): DataFrame with 'AbsoluteTime' (timezone-aware UTC) and the target column (e.g., 'HR').
        task_file (str): Path to the task timing file (semicolon-separated).
        value_col (str): The name of the column in df to calculate statistics on (default: 'HR').

    Returns:
        pd.DataFrame: Summary results for each task.
    """
    # Load and clean task timing file
    df_tasks = pd.read_csv(task_file, sep=';', skipinitialspace=True, header=0, dtype=str, keep_default_na=False)
    df_tasks.columns = [col.strip() for col in df_tasks.columns]
    df_tasks = df_tasks.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    results = []
    local_tz = pytz.timezone('Europe/London')  # BST (handles DST)

    for idx, row in df_tasks.iterrows():
        subject_id = row['ID']
        date_str = row['date']

        for task_num in range(1, 4):
            start_col = f'task{task_num}_st'
            end_col = f'task{task_num}_et'

            st_str = row.get(start_col, '').strip()
            et_str = row.get(end_col, '').strip()

            # If missing task times
            if st_str == '' or et_str == '':
                results.append({
                    'Subject': subject_id,
                    'Task': f'Task{task_num}',
                    'Start': pd.NaT,
                    'End': pd.NaT,
                    f'Mean_{value_col}': np.nan,
                    f'STD_{value_col}': np.nan,
                    f'Min_{value_col}': np.nan,
                    f'Max_{value_col}': np.nan,
                    f'Median_{value_col}': np.nan,
                    f'Mode_{value_col}': np.nan,
                    'Samples': 0
                })
                continue

            # Parse start and end times (try both with seconds and without)
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
                results.append({
                    'Subject': subject_id,
                    'Task': f'Task{task_num}',
                    'Start': task_start,
                    'End': task_end,
                    f'Mean_{value_col}': np.nan,
                    f'STD_{value_col}': np.nan,
                    f'Min_{value_col}': np.nan,
                    f'Max_{value_col}': np.nan,
                    f'Median_{value_col}': np.nan,
                    f'Mode_{value_col}': np.nan,
                    'Samples': 0
                })
                continue

            # Localize to BST then convert to UTC
            task_start = local_tz.localize(task_start).astimezone(pytz.utc)
            task_end = local_tz.localize(task_end).astimezone(pytz.utc)

            # Filter task data
            if value_col not in df.columns:
                filtered_df = pd.DataFrame()
            else:
                filtered_df = df[(df['AbsoluteTime'] >= task_start) & (df['AbsoluteTime'] <= task_end)]

            # Calculate stats
            if not filtered_df.empty:
                values = filtered_df[value_col].dropna().values
                mean_val = np.mean(values)
                std_val = np.std(values, ddof=1)
                min_val = np.min(values)
                max_val = np.max(values)
                median_val = np.median(values)
                try:
                    mode_val = mode(values, keepdims=True).mode[0]
                except:
                    mode_val = np.nan
                sample_count = len(values)
            else:
                mean_val = std_val = min_val = max_val = median_val = mode_val = np.nan
                sample_count = 0

            results.append({
                'Subject': subject_id,
                'Task': f'Task{task_num}',
                'Start': task_start,
                'End': task_end,
                f'Mean_{value_col}': mean_val,
                f'STD_{value_col}': std_val,
                f'Min_{value_col}': min_val,
                f'Max_{value_col}': max_val,
                f'Median_{value_col}': median_val,
                f'Mode_{value_col}': mode_val,
                'Samples': sample_count
            })
        #print(df)
    return pd.DataFrame(results)
