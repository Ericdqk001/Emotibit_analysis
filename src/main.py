from pathlib import Path

import pandas as pd
from src.scripts.preprocess import calculate_row_average

data_store_path = Path(
    "/",
    "Volumes",
    "INT-ACT",
)

code_example_path = Path(
    data_store_path,
    "coding example_icmiPaper",
)

input_data_path = Path(
    code_example_path,
    "wrist",
    "2025-05-12_22-05-22-738924.csv",
)

df_raw = pd.read_csv(
    input_data_path,
    header=None,
    engine="python",
    sep=",",
    names=[f"col_{i}" for i in range(30)],
    skip_blank_lines=True,
)

df_raw["AverageDataValue"] = df_raw.apply(
    calculate_row_average,  # type: ignore
    axis=1,
)
