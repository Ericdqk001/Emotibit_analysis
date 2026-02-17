"""Visualize EmotiBit sensor data.

Creates:
1. Time series plots (signal over time)
2. Recording overview (all sensors in one figure)
3. Distribution plots (histograms)
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# Sensor display names and units
SENSOR_INFO = {
    "EA": ("EDA Amplitude", "μS"),
    "EL": ("EDA Level", "raw"),
    "HR": ("Heart Rate", "bpm"),
    "T1": ("Temperature 1", "°C"),
    "TH": ("Temperature H", "°C"),
    "PI": ("PPG Infrared", "raw"),
    "PR": ("PPG Red", "raw"),
    "PG": ("PPG Green", "raw"),
}


def plot_time_series(
    df: pd.DataFrame,
    sensor: str,
    output_path: Path | None = None,
) -> None:
    """Plot time series for a single sensor."""
    name, unit = SENSOR_INFO.get(sensor, (sensor, ""))

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(df["Time_s"], df[sensor], linewidth=0.5)
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel(f"{name} ({unit})")
    ax.set_title(f"{name} over time")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150)
        print(f"Saved: {output_path.name}")
        plt.close()
    else:
        plt.show()


def plot_recording_overview(
    data: dict[str, pd.DataFrame],
    title: str = "",
    output_path: Path | None = None,
) -> None:
    """Create multi-panel figure showing all sensors."""
    sensors = list(data.keys())
    n_sensors = len(sensors)

    fig, axes = plt.subplots(n_sensors, 1, figsize=(14, 2 * n_sensors), sharex=True)
    if n_sensors == 1:
        axes = [axes]

    for ax, sensor in zip(axes, sensors, strict=False):
        df = data[sensor]
        name, unit = SENSOR_INFO.get(sensor, (sensor, ""))

        ax.plot(df["Time_s"], df[sensor], linewidth=0.5)
        ax.set_ylabel(f"{name}\n({unit})", fontsize=9)
        ax.grid(True, alpha=0.3)

    axes[-1].set_xlabel("Time (seconds)")
    if title:
        fig.suptitle(title, fontsize=12, fontweight="bold")

    plt.tight_layout()
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150)
        print(f"Saved: {output_path.name}")
        plt.close()
    else:
        plt.show()


def plot_distribution(
    df: pd.DataFrame,
    sensor: str,
    output_path: Path | None = None,
) -> None:
    """Plot histogram of sensor values."""
    name, unit = SENSOR_INFO.get(sensor, (sensor, ""))
    values = df[sensor].dropna()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(values, bins=50, edgecolor="black", alpha=0.7)
    ax.set_xlabel(f"{name} ({unit})")
    ax.set_ylabel("Frequency")
    ax.set_title(f"{name} Distribution")
    ax.grid(True, alpha=0.3)

    # Add stats annotation
    stats_text = f"n={len(values):,}\nmean={values.mean():.2f}\nstd={values.std():.2f}"
    ax.text(
        0.95,
        0.95,
        stats_text,
        transform=ax.transAxes,
        verticalalignment="top",
        horizontalalignment="right",
        fontsize=9,
        # bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )

    plt.tight_layout()
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150)
        print(f"Saved: {output_path.name}")
        plt.close()
    else:
        plt.show()


if __name__ == "__main__":
    import sys

    from load_data import discover_recordings, load_recording

    base_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None

    if base_path and base_path.exists():
        recordings = discover_recordings(base_path)
        if recordings:
            r = recordings[0]
            print(f"Visualizing: {r.day}/{r.pair_id}/{r.participant}\n")

            data = load_recording(r.path, r.timestamp)
            output_dir = Path(__file__).parent.parent / "outputs"

            # 1. Recording overview
            plot_recording_overview(
                data,
                title=f"{r.pair_id} / {r.participant} / {r.day}",
                output_path=output_dir
                / f"{r.pair_id}_{r.participant}_{r.day}_overview.png",
            )

            # 2. Individual time series for key sensors
            for sensor in ["HR", "EA", "T1"]:
                if sensor in data:
                    plot_time_series(
                        data[sensor],
                        sensor,
                        output_path=output_dir
                        / f"{r.pair_id}_{r.participant}_{r.day}_{sensor}.png",
                    )

            # 3. Distribution for HR
            if "HR" in data:
                plot_distribution(
                    data["HR"],
                    "HR",
                    output_path=output_dir
                    / f"{r.pair_id}_{r.participant}_{r.day}_HR_dist.png",
                )

            print(f"\nAll plots saved to: {output_dir}")
        else:
            print("No recordings found")
    else:
        print("Usage: python visualize.py <emotibit_base_path>")
