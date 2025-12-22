import pandas as pd
import os
from datetime import datetime
import pytz

def load_emotibit_sensor(input_csv, sensor_type):
    """
    Load EmotiBit CSV for a specific sensor type, parse time columns.

    Args:
        input_csv (str): Path to EmotiBit CSV file.
        sensor_type (str): The TypeTag or column name (e.g., 'HR', 'AX', 'AY', 'PG').

    Returns:
        pd.DataFrame: DataFrame for the sensor with AbsoluteTime and relative Time_s.
    """
    # ===== Extract Start Time from Filename =====
    filename = os.path.basename(input_csv)
    filename_wo_ext = filename.replace('.csv', '')

    if '_' in filename_wo_ext:
        st_str = '_'.join(filename_wo_ext.split('_')[:-1])  # Drop sensor tag at the end
    else:
        raise ValueError(f"Filename format unexpected: {filename}")

    try:
        start_time = datetime.strptime(st_str, '%Y-%m-%d_%H-%M-%S-%f')
    except ValueError:
        raise ValueError(f"Failed to parse datetime from filename: {st_str}")

    # ===== Load CSV =====
    df = pd.read_csv(input_csv)
    df['LocalTimestamp'] = pd.to_numeric(df['LocalTimestamp'], errors='coerce')
    df = df.dropna(subset=['LocalTimestamp'])

    # ===== Filter by Sensor Type =====
    if 'TypeTag' in df.columns:
        df_sensor = df[df['TypeTag'] == sensor_type].copy()
    else:
        df_sensor = df.copy()

    if df_sensor.empty:
        print(f"Warning: No data found for sensor '{sensor_type}' in file {input_csv}")
        return df_sensor

    # ===== Convert LocalTimestamp to UTC datetime =====
    df_sensor['AbsoluteTime'] = pd.to_datetime(df_sensor['LocalTimestamp'], unit='s', utc=True)

    # ===== Relative Time in Seconds =====
    first_local_timestamp = df_sensor['LocalTimestamp'].iloc[0]
    df_sensor['Time_s'] = df_sensor['LocalTimestamp'] - first_local_timestamp


    return df_sensor
