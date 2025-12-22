import os

import pandas as pd
from src.code_examples.emotibit_task_analysis import calculate_task_stats
from src.code_examples.loading_data import load_emotibit_sensor
from stat_test import calculate_task_ttests


def process_wrist_sensor_data(
    sensor_type,
    task_file="task_times.txt",
    subject_ids=["SL", "FH", "SDLF", "Ali"],
    base_folder="./wrist/",
):
    """Process wrist EmotiBit data for a given sensor type and return task-level stats for all subjects.

    Parameters:
    - sensor_type (str): e.g., 'HR', 'AX', 'AY', 'PG'
    - task_file (str): Path to the task times file
    - subject_ids (list): List of subject IDs matching folder names
    - base_folder (str): Base path where subject folders exist

    Returns:
    - df_final (pd.DataFrame): Summary with Mean, STD, Min, Max, Median, Mode, Samples, etc. for each task per subject
    """
    all_dfs = []

    for subject in subject_ids:
        # Find CSV file for this subject and sensor type
        folder = os.path.join(base_folder, subject)
        file_list = [f for f in os.listdir(folder) if f.endswith(f"_{sensor_type}.csv")]

        if not file_list:
            print(
                f"Warning: No {sensor_type} file found for subject {subject} in {folder}"
            )
            continue

        input_csv = os.path.join(folder, file_list[0])

        # Load and process
        df_subject = load_emotibit_sensor(input_csv, sensor_type=sensor_type)
        df_results = calculate_task_stats(df_subject, task_file, value_col=sensor_type)
        df_ttest = calculate_task_ttests(
            df_subject, task_file, value_col=sensor_type, subject_id=subject
        )

        all_dfs.append(df_results)
        print(df_ttest)
    # === Combine all dataframes ===
    if not all_dfs:
        print("No dataframes loaded. Returning empty dataframe.")
        return pd.DataFrame()

    # Start with first subject's dataframe
    df_final = all_dfs[0].copy()

    # Identify all metrics/statistics columns dynamically (all except Subject, Task, Start, End)
    metrics_cols = [
        col
        for col in df_final.columns
        if col not in ["Subject", "Task", "Start", "End"]
    ]

    # Loop through the rest of the subjects' dataframes and fill missing stats
    for df_next in all_dfs[1:]:
        for idx, row in df_final.iterrows():
            subject = row["Subject"]
            task = row["Task"]
            match = df_next[(df_next["Subject"] == subject) & (df_next["Task"] == task)]
            if not match.empty:
                match_row = match.iloc[0]
                for col in metrics_cols:
                    # Fill missing or zero-sample values
                    if pd.isna(row[col]) or (col == "Samples" and row[col] == 0):
                        df_final.at[idx, col] = match_row[col]

    return df_final
