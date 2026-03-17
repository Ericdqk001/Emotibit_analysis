"""Visualization of EmotiBit descriptive statistics.

Creates academic-style boxplots of sensor mean values (HR, EA, PG)
across participants, grouped by day. CS2 and MCI data are combined.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SENSORS = {
    "HR": {"label": "Heart Rate", "title": "HR"},
    "EA": {"label": "Electrodermal Activity", "title": "EDA"},
    "PG": {"label": "PPG Green", "title": "PG"},
}


def load_combined_stats(cs2_path: Path, mci_path: Path) -> pd.DataFrame:
    """Load and combine CS2 and MCI descriptive stats."""
    cs2 = pd.read_csv(cs2_path)
    cs2["study"] = "CS2"
    mci = pd.read_csv(mci_path)
    mci["study"] = "MCI"

    cols = [
        "day",
        "participant",
        "sensor",
        "study",
        "mean",
        "std",
        "min",
        "q25",
        "median",
        "q75",
        "max",
    ]
    combined: pd.DataFrame = pd.concat([cs2[cols], mci[cols]], ignore_index=True)  # type: ignore[assignment]
    return combined


def set_academic_style() -> None:
    """Configure matplotlib for publication-quality figures."""
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 11,
            "axes.labelsize": 12,
            "axes.titlesize": 13,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.8,
            "xtick.major.width": 0.8,
            "ytick.major.width": 0.8,
        }
    )


def plot_sensor_boxplots_by_day(df: pd.DataFrame, output_dir: Path) -> None:
    """Create boxplots of sensor means grouped by day.

    One subplot per sensor (HR, EA, PG), with day1 and day2 side by side.
    """
    fig, axes = plt.subplots(1, 3, figsize=(10, 4))

    for ax, (sensor, info) in zip(axes, SENSORS.items(), strict=False):
        sensor_data = df[df["sensor"] == sensor]

        day1: pd.Series = sensor_data[sensor_data["day"] == "day1"]["mean"]  # type: ignore[assignment]
        day2: pd.Series = sensor_data[sensor_data["day"] == "day2"]["mean"]  # type: ignore[assignment]

        ax.boxplot(
            [day1.dropna(), day2.dropna()],
            labels=["Day 1", "Day 2"],
            widths=0.5,
            patch_artist=True,
            boxprops={"facecolor": "white", "edgecolor": "black", "linewidth": 0.8},
            medianprops={"color": "black", "linewidth": 1.2},
            whiskerprops={"linewidth": 0.8},
            capprops={"linewidth": 0.8},
            flierprops={
                "marker": "o",
                "markersize": 4,
                "markerfacecolor": "none",
                "markeredgecolor": "black",
            },
        )

        ax.set_ylabel(info["label"])
        ax.set_title(info["title"])

    fig.suptitle(
        "Physiological Signal Mean Values by Day",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )
    plt.tight_layout()

    path = output_dir / "boxplot_sensors_by_day.png"
    fig.savefig(path)
    print(f"Saved: {path}")
    plt.close(fig)


def plot_sensor_boxplots_by_study(df: pd.DataFrame, output_dir: Path) -> None:
    """Create boxplots of sensor means grouped by study (CS2 vs MCI).

    One subplot per sensor, with CS2 and MCI side by side.
    """
    fig, axes = plt.subplots(1, 3, figsize=(10, 4))

    for ax, (sensor, info) in zip(axes, SENSORS.items(), strict=False):
        sensor_data = df[df["sensor"] == sensor]

        cs2: pd.Series = sensor_data[sensor_data["study"] == "CS2"]["mean"]  # type: ignore[assignment]
        mci: pd.Series = sensor_data[sensor_data["study"] == "MCI"]["mean"]  # type: ignore[assignment]

        ax.boxplot(
            [cs2.dropna(), mci.dropna()],
            labels=["CS2", "MCI"],
            widths=0.5,
            patch_artist=True,
            boxprops={"facecolor": "white", "edgecolor": "black", "linewidth": 0.8},
            medianprops={"color": "black", "linewidth": 1.2},
            whiskerprops={"linewidth": 0.8},
            capprops={"linewidth": 0.8},
            flierprops={
                "marker": "o",
                "markersize": 4,
                "markerfacecolor": "none",
                "markeredgecolor": "black",
            },
        )

        ax.set_ylabel(info["label"])
        ax.set_title(info["title"])

    fig.suptitle("Sensor Mean Values by Study", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()

    path = output_dir / "boxplot_sensors_by_study.png"
    fig.savefig(path)
    print(f"Saved: {path}")
    plt.close(fig)


def plot_sensor_boxplots_by_day_and_study(df: pd.DataFrame, output_dir: Path) -> None:
    """Create boxplots with 4 groups per sensor."""
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.5))

    groups = [
        ("CS2\nDay 1", "CS2", "day1"),
        ("CS2\nDay 2", "CS2", "day2"),
        ("MCI\nDay 1", "MCI", "day1"),
        ("MCI\nDay 2", "MCI", "day2"),
    ]

    for ax, (sensor, info) in zip(axes, SENSORS.items(), strict=False):
        sensor_data = df[df["sensor"] == sensor]

        data = []
        labels = []
        for label, study, day in groups:
            subset: pd.Series = sensor_data[
                (sensor_data["study"] == study) & (sensor_data["day"] == day)
            ]["mean"]  # type: ignore[assignment]
            data.append(subset.dropna())
            labels.append(label)

        ax.boxplot(
            data,
            labels=labels,
            widths=0.5,
            patch_artist=True,
            boxprops={"facecolor": "white", "edgecolor": "black", "linewidth": 0.8},
            medianprops={"color": "black", "linewidth": 1.2},
            whiskerprops={"linewidth": 0.8},
            capprops={"linewidth": 0.8},
            flierprops={
                "marker": "o",
                "markersize": 4,
                "markerfacecolor": "none",
                "markeredgecolor": "black",
            },
        )

        ax.set_ylabel(info["label"])
        ax.set_title(info["title"])

    fig.suptitle(
        "Sensor Mean Values by Study and Day", fontsize=14, fontweight="bold", y=1.02
    )
    plt.tight_layout()

    path = output_dir / "boxplot_sensors_by_day_and_study.png"
    fig.savefig(path)
    print(f"Saved: {path}")
    plt.close(fig)


def plot_correlation_heatmap(r_values_path: Path, day: str, output_dir: Path) -> None:
    """Create a correlation heatmap from r-values CSV.

    Replicates the style from the speech PCA correlation figures:
    red-blue diverging colormap, bold white text for |r| >= 0.4,
    VAS Labels xlabel, auto-scaling color range.
    """
    r_matrix = pd.read_csv(r_values_path, index_col="sensor")

    # Sort columns alphabetically to match reference style
    r_matrix = r_matrix.reindex(sorted(r_matrix.columns), axis=1)

    # Format labels to match reference: "Negative_Affect", "VAS_belonging", etc.
    col_labels = []
    for c in r_matrix.columns:
        if c.startswith("VAS_"):
            col_labels.append(c)
        else:
            # positive_affect -> Positive_Affect
            col_labels.append(c.replace("_", " ").title().replace(" ", "_"))

    row_labels = [s.replace("_mean", "").replace("EA", "EDA") for s in r_matrix.index]

    data = r_matrix.values.astype(float)
    n_rows, n_cols = data.shape

    # Auto-scale color range symmetrically around 0
    abs_max = max(abs(data.min()), abs(data.max()))
    vbound = round(abs_max + 0.1, 1)  # round up with small padding

    fig, ax = plt.subplots(figsize=(n_cols * 1.2 + 1.5, n_rows * 1.0 + 1.5))

    # Use default sans-serif font for this plot (matching reference)
    with plt.rc_context({"font.family": "sans-serif"}):
        im = ax.imshow(data, cmap="RdBu_r", vmin=-vbound, vmax=vbound, aspect="auto")

        # Annotate each cell
        for i in range(n_rows):
            for j in range(n_cols):
                val = data[i, j]
                weight = "bold" if abs(val) >= 0.4 else "normal"
                color = "white" if abs(val) >= 0.45 else "black"
                ax.text(
                    j,
                    i,
                    f"{val:.2f}",
                    ha="center",
                    va="center",
                    fontsize=11,
                    fontweight=weight,
                    color=color,
                )

        # Axes
        ax.set_xticks(np.arange(n_cols))
        ax.set_yticks(np.arange(n_rows))
        ax.set_xticklabels(col_labels, rotation=45, ha="right", fontsize=10)
        ax.set_yticklabels(row_labels, fontsize=10)

        ax.set_xlabel("VAS and PANAS Measures", fontsize=12)
        ax.set_ylabel("Signal Means", fontsize=12)

        day_label = day.replace("day", "Day ")
        ax.set_title(
            f"Pearson Correlation: Signals vs Survey ({day_label})",
            fontsize=13,
            fontweight="bold",
            pad=12,
        )

        # Colorbar
        cbar = fig.colorbar(im, ax=ax, shrink=0.8)
        cbar.ax.tick_params(labelsize=9)

        # Remove spines
        for spine in ax.spines.values():
            spine.set_visible(False)

        plt.tight_layout()

    path = output_dir / f"correlation_heatmap_{day}.png"
    fig.savefig(path)
    print(f"Saved: {path}")
    plt.close(fig)


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent.parent

    cs2_path = (
        project_root
        / "src"
        / "emotibit"
        / "output"
        / "emotibit_CS2_descriptive_stats.csv"
    )
    mci_path = project_root / "src" / "MCI" / "output" / "mci_descriptive_stats.csv"
    output_dir = script_dir.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    for path, name in [(cs2_path, "CS2 stats"), (mci_path, "MCI stats")]:
        if not path.exists():
            print(f"Error: {name} not found at {path}")
            sys.exit(1)

    set_academic_style()

    df = load_combined_stats(cs2_path, mci_path)
    print(f"Loaded {len(df)} rows ({df['study'].value_counts().to_dict()})")

    # Exclude participants with saturated EA values (max == 10000)
    # ea_saturated = df[(df["sensor"] == "EA") & (df["max"] == 10000.0)]
    # bad_keys = set(zip(ea_saturated["day"], ea_saturated["participant"]))
    # if bad_keys:
    #     print(f"\nExcluding {len(bad_keys)} saturated EA:")
    #     for day, pid in sorted(bad_keys):
    #         print(f"  {day}/{pid}")
    #     df = df[~df.apply(lambda r: (r["day"], r["participant"]) in bad_keys, axis=1)]
    #     print(f"Remaining: {len(df)} rows")

    plot_sensor_boxplots_by_day(df, output_dir)
    plot_sensor_boxplots_by_study(df, output_dir)
    plot_sensor_boxplots_by_day_and_study(df, output_dir)

    # Correlation heatmaps
    for day in ["day1", "day2"]:
        r_path = output_dir / f"correlation_{day}_r_values.csv"
        if r_path.exists():
            plot_correlation_heatmap(r_path, day, output_dir)
        else:
            print(f"Skipping {day} heatmap: {r_path.name} not found")
