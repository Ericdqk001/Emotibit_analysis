# from pathlib import Path

# import pandas as pd
# from src.scripts.align import align_axes
# from src.scripts.preprocess import calculate_row_average

# print("Starting EmotiBit data parsing...")

# # data_store_path = Path(
# #     "/",
# #     "Volumes",
# #     "INT-ACT",
# # )

# # code_example_path = Path(
# #     data_store_path,
# #     "coding example_icmiPaper",
# # )

# input_data_path = Path(
#     # code_example_path,
#     "wrist",
#     "2025-05-12_22-05-22-738924.csv",
# )

# output_folder = Path("modular_parsed_sensor_csvs")
# output_folder.mkdir(parents=True, exist_ok=True)

# df_raw = pd.read_csv(
#     input_data_path,
#     header=None,
#     engine="python",
#     sep=",",
#     names=[f"col_{i}" for i in range(30)],
#     skip_blank_lines=True,
# )

# df_raw["AverageDataValue"] = df_raw.apply(
#     calculate_row_average,  # type: ignore
#     axis=1,
# )

# df = df_raw.iloc[:, :7]

# df.columns = [
#     "EmotiBitTimestamp",
#     "PacketNumber",
#     "DataLength",
#     "TypeTag",
#     "ProtocolVersion",
#     "DataReliability",
#     "Data",
# ]
# df["AverageDataValue"] = df_raw["AverageDataValue"]
# df = df[~df["TypeTag"].isin(["EM", "RB"])].reset_index(drop=True)

# df_expanded = df.copy()
# df_expanded = df_expanded.dropna(subset=["Data"])

# # Not needed as the data was separated by commas already
# # Just rename Data for Data_0
# df_expanded = df_expanded.rename(columns={"Data": "Data_0"})

# print("Start aligning and saving sensor data...")

# ### ALIGN AND SAVE EACH MULTI-AXIS SENSOR
# for sensor in ["A", "G", "M"]:  # A=Accel, G=Gyro, M=Magnetometer
#     if all(
#         (sensor + axis) in df_expanded["TypeTag"].values for axis in ["X", "Y", "Z"]
#     ):
#         aligned = align_axes(df_expanded, sensor)
#         filename = {
#             "A": "Accelerometer",
#             "G": "Gyroscope",
#             "M": "Magnetometer",
#         }[sensor]
#         aligned.to_csv(
#             Path(output_folder, f"EmotiBit_{filename}_Aligned.csv"),
#             index=False,
#         )
#         print(f"Saved {filename} aligned CSV.")

# ### SINGLE CHANNEL SENSORS (EDA, TEMP, etc)
# # EA = EDA (Electrodermal Activity), EL = EDL (Electrodermal Level)
# # T1 = Temperature 1, TH = Temperature via Medical-grade Thermopile
# # HR = Heart Rate, SF = Skin Conductance Response Frequency, BI = Inter-Beat Interval
# single_channel_sensors = ["EA", "EL", "T1", "TH", "HR", "SF", "BI"]

# for sensor in single_channel_sensors:
#     if sensor in df_expanded["TypeTag"].values:
#         sensor_df = df_expanded[df_expanded["TypeTag"] == sensor][
#             ["EmotiBitTimestamp", "Data_0"]
#         ].rename(columns={"Data_0": sensor})

#         sensor_df.to_csv(
#             Path(output_folder, f"EmotiBit_{sensor}_Raw.csv"),
#             index=False,
#         )

#         print(f"Saved {sensor} raw CSV.")
