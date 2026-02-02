import numpy as np
import pandas as pd


def calculate_row_average(row: pd.Series) -> float | np.floating:
    """Calculate the mean of data points.

    Data points start from index 6 (Payload).
    For details on raw data format, read:
    https://github.com/EmotiBit/EmotiBit_Docs/blob/master/Working_with_emotibit_data.md

    Args:
        row: A single row from the EmotiBit DataFrame.

    Returns:
        Mean of valid numeric values, or np.nan if none found.
    """
    values = []
    for col in row.index[6:]:  # type: ignore[union-attr]
        val = row[col]
        try:
            if pd.notna(val) is True:
                values.append(float(val))
        except (ValueError, TypeError):
            continue

    if values:
        return np.mean(values)
    else:
        return np.nan
