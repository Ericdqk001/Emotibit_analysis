# import pandas as pd


# def align_axes(
#     df,
#     base_tag,
#     axes=None,
# ):
#     """Merge multi-axis sensor data by aligning timestamps.

#     EmotiBit sends each axis (X, Y, Z) as separate rows. This function
#     combines them into a single DataFrame where each row contains all
#     axes at the same time point, using nearest-timestamp matching.

#     Args:
#         df (pd.DataFrame): DataFrame.
#         base_tag (str): Sensor prefix, e.g., 'A' for Accelerometer (AX, AY, AZ).
#         axes (list[str], optional): Axis suffixes to align.
#         Defaults to ["X", "Y", "Z"].

#     Returns:
#         pd.DataFrame: Aligned DataFrame with columns [EmotiBitTimestamp, X, Y, Z].
#     """
#     if axes is None:
#         axes = ["X", "Y", "Z"]

#     axis_dfs = []
#     for axis in axes:
#         tag = f"{base_tag}{axis}"
#         axis_df = df[df["TypeTag"] == tag][["EmotiBitTimestamp", "Data_0"]].copy()
#         axis_df = axis_df.rename(columns={"Data_0": axis})
#         axis_df["EmotiBitTimestamp"] = pd.to_numeric(
#             axis_df["EmotiBitTimestamp"], errors="coerce"
#         )
#         axis_dfs.append(axis_df.sort_values("EmotiBitTimestamp"))

#     # Start with first axis dataframe
#     aligned_df = axis_dfs[0]
#     for _, other_axis_df in enumerate(axis_dfs[1:], start=1):
#         aligned_df = pd.merge_asof(
#             aligned_df.sort_values("EmotiBitTimestamp"),
#             other_axis_df.sort_values("EmotiBitTimestamp"),
#             on="EmotiBitTimestamp",
#             direction="nearest",
#             tolerance=0.02,  # 20 ms tolerance (adjust if needed)
#         )

#     # NOTE: 0.02 here is the wrong type for the argument, if we want 20ms, the value
#     # should be an integer 20 or pd.Timedelta("20ms")
#     aligned_df = aligned_df.dropna()
#     return aligned_df
